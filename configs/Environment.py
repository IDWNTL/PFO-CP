from functools import lru_cache

from pydantic_settings import BaseSettings


class EnvironmentSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    DEBUG: bool

    MINIO_HOST: str
    MINIO_ACCESS: str
    MINIO_SECRET: str
    MINIO_BASE_BUCKET: str

    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: str
    CLICKHOUSE_DATABASE: str

    YANDEX_FOLDER_ID: str
    YANDEX_TOKEN: str

    ENV: str

    class Config:
        env_file = "configs/.env"
        env_file_encoding = "utf-8"


@lru_cache
def get_environment_variables() -> EnvironmentSettings:
    return EnvironmentSettings()
