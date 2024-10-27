from typing import BinaryIO

import torch.nn.functional
from PIL import Image
from loguru import logger

from ml.embedders import EmbeddingGenerator


class MlRepository:
    def __init__(self):
        self._embeder = EmbeddingGenerator()

    def get_embeddings_from_text(self, texts: list[str]) -> list[float]:
        logger.debug("ML - Repository - get_embeddings_from_text")
        emb = self._embeder.get_text_embedding(texts)

        return emb.squeeze().tolist()

    def get_metric(self, text1: str, text2: str) -> float:
        logger.debug("ML - Repository - get_metric")
        emb1 = self._embeder.get_text_embedding([text1])
        emb2 = self._embeder.get_text_embedding([text2])

        sim = torch.nn.functional.cosine_similarity(emb1, emb2, dim=1)

        return float(sim)

    def get_embeddings_from_image(self, image: BinaryIO):
        logger.debug("ML - Repository - get_embeddings_from_image")
        image = Image.open(image)
        embeddings = self._embeder.get_image_embedding([image])

        embeddings = embeddings.squeeze().tolist()

        return embeddings
