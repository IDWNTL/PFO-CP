from loguru import logger
from minio import Minio

from configs.Environment import get_environment_variables
from ml.indexing import docs2clickhouse
from repositories.clickhouse import ClickhouseRepository
from services.minio import MinioService

repo = ClickhouseRepository()

env = get_environment_variables()

minio_client = Minio(
    env.MINIO_HOST,
    access_key=env.MINIO_ACCESS,
    secret_key=env.MINIO_SECRET,
    secure=False if env.ENV == "LOCAL" else True,
)

static_storage = MinioService(minio_client)

# embedding_generator = EmbeddingGenerator()
#
# emb = embedding_generator.get_text_embedding(["С чего начать работу"])
#
#
# res = repo.get_chunk_by_emb(emb.squeeze().tolist(), 5)
#
# print(res)

if __name__ == "__main__":
    docx_path = "ml/test_data/data.docx"
    try:
        docs2clickhouse(repo, static_storage, docx_path)
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке: {e}")
