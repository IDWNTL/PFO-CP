import json
import uuid

from loguru import logger

from configs.Clickhouse import client
from errors.errors import ErrEntityNotFound
from schemas.clickhouse import (
    CreateChunkOpts,
    CreateParagraphOpts,
    ParagraphSchema,
    ChunkWithoutEmb,
)


class ClickhouseRepository:
    def __init__(self):
        self._client = client

    def create_chunk(self, opts: CreateChunkOpts):
        logger.debug("Clickhouse - Repository - create_chunk")
        query = """
            INSERT INTO `chunk` (id, emb, text, paragraph_id)
            VALUES (%s, %s, %s, %s)   
        """

        self._client.command(
            query,
            (
                opts.id,
                opts.emb,
                opts.text,
                opts.paragraph_id,
            ),
        )

    def create_paragraph(self, opts: CreateParagraphOpts):
        logger.debug("Clickhouse - Repository - create_paragraph")
        query = """
            INSERT INTO `paragraph` (id, name, text, num, images)
            VALUES (%s, %s, %s, %s, %s)   
        """

        self._client.command(
            query,
            (
                opts.id,
                opts.num,
                opts.text,
                opts.num,
                json.dumps(opts.images).replace('"', "'"),
            ),
        )

    def get_chunk_by_emb(
        self, embeddings: list[float], top_k: int
    ) -> list[ChunkWithoutEmb]:
        logger.debug("Clickhouse - Repository - get_chunk_by_emb")
        query = f"""
            WITH {embeddings} as query_vector
            SELECT id, text, paragraph_id, cosine_similarity, 
            arraySum(x -> x * x, emb) * arraySum(x -> x * x, query_vector) != 0
            ? arraySum((x, y) -> x * y, emb, query_vector) / sqrt(arraySum(x -> x * x, emb) * arraySum(x -> x * x, query_vector))
            : 0 AS cosine_similarity
            FROM chunk
            WHERE length(query_vector) == length(emb)
            ORDER BY cosine_similarity DESC 
            LIMIT {top_k}
        """

        result = self._client.query(
            query, settings={"max_query_size": "10000000000000"}
        )

        rows = result.result_rows

        chunks = []

        for row in rows:
            chunks.append(
                ChunkWithoutEmb(
                    id=row[0], text=row[1], paragraph_id=row[2], cos_dist=row[3]
                )
            )

        return chunks

    def get_paragraph(self, id: uuid.UUID) -> ParagraphSchema:
        logger.debug("Clickhouse - Repository - get_paragraph")
        query = """
            SELECT id, name, text, num, images FROM paragraph
            WHERE id = %s
        """

        row = self._client.command(query, (id,))

        if row:
            return ParagraphSchema(
                id=row[0],
                name=row[1],
                text=row[2],
                num=row[3],
                images=json.loads(row[4].replace("'", '"')),
            )
        else:
            raise ErrEntityNotFound(f"there is no paragraph with id {id}")
