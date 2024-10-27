import shutil
from tempfile import NamedTemporaryFile
from typing import BinaryIO

import torch
from fastapi import Depends, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from configs.YandexGPT import yandexGPT
from ml.classificators.swear_classifier import has_swear
from ml.classificators.toxic_classifier import is_toxic
from ml.constants import SYSTEM_PROMPT, USER_PROMPT
from ml.indexing import docs2clickhouse
from ml.lifespan import toxic_clf, swear_clf
from repositories.clickhouse import ClickhouseRepository
from repositories.ml import MlRepository
from schemas.clickhouse import AnswerResponse
from services.minio import MinioService


class MlService:
    def __init__(
        self,
        clickhouse: ClickhouseRepository = Depends(),
        minio: MinioService = Depends(),
        repo: MlRepository = Depends(),
    ):
        self._clickhouse = clickhouse

        self._repo = repo

        self._minio = minio

        self._top_k = 5

        self._llm = yandexGPT

        self._llm_retries = 3

    def indexing(self, file: BinaryIO):
        logger.debug("ML - Service - indexing")
        try:
            with NamedTemporaryFile(delete=True, suffix=".docx") as temp_file:
                shutil.copyfileobj(file, temp_file)
                temp_file.flush()

                docs2clickhouse(self._clickhouse, self._minio, temp_file.name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_answer(self, question: str, image: BinaryIO | None) -> AnswerResponse:
        logger.debug("ML - Service - get_answer")
        answer = "Извините, я не уверена, что поняла ваш вопрос. Можете уточнить или переформулировать его?"

        if is_toxic(toxic_clf, question) or has_swear(swear_clf, question):
            return AnswerResponse(answer=answer, images=[])

        embeddings = self._repo.get_embeddings_from_text([question])

        if image:
            image_embeddings = self._repo.get_embeddings_from_image(image)

            embeddings = (torch.Tensor(embeddings) + torch.Tensor(image_embeddings)) / 2

            embeddings = embeddings.tolist()

        chunks = self._clickhouse.get_chunk_by_emb(embeddings, self._top_k)

        chunk = chunks[0]

        if 0.7 < chunk.cos_dist < 0.8:
            answer = self._llm.invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(
                        content=USER_PROMPT.format(
                            "Данные не найдены", "Данные не найдены", question
                        )
                    ),
                ]
            ).content

            logger.info(
                f"answer = {answer} \n\n chunk = {chunk}, 0.8 < chunk.cos_dist < 0.9"
            )

            return AnswerResponse(
                answer=answer,
                images=[],
            )

        elif chunk.cos_dist < 0.7:
            answer = self._llm.invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(
                        content=USER_PROMPT.format(
                            "Обратитесь к технической поддержке",
                            "Обратитесь к технической поддержке",
                            question,
                        )
                    ),
                ]
            ).content

            logger.info(f"answer = {answer} \n chunk = {chunk}, chunk.cos_dist < 0.8")

            return AnswerResponse(
                answer=answer,
                images=[],
            )

        paragraph = self._clickhouse.get_paragraph(chunk.paragraph_id)

        for i in range(self._llm_retries):
            local_answer = self._llm.invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(
                        content=USER_PROMPT.format(paragraph.text, chunk.text, question)
                    ),
                ]
            ).content

            metric = self._repo.get_metric(paragraph.text, local_answer)
            logger.info(
                f"answer = {local_answer} \n chunk = {chunk} \n\n paragraph = {paragraph.text} \n\n metric = {metric}"
            )

            if (
                metric > 0.4
                and not is_toxic(toxic_clf, local_answer)
                and not has_swear(swear_clf, local_answer)
            ):
                answer = local_answer
                break

        return AnswerResponse(
            answer=answer,
            images=[self._minio.get_link(path) for _, path in paragraph.images.items()],
        )
