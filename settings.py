import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: Optional[str] = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: Optional[int] = Field(default=3000, alias="APP_PORT")
    app_debug: Optional[bool] = Field(default=False, alias="APP_DEBUG")
    db_url: str = Field(default=..., alias="DB_URL")
    max_file_upload_count: Optional[int] = Field(
        default=5, alias="MAX_FILE_UPLOAD_COUNT"
    )
    max_file_bytes_size: Optional[int] = Field(
        default=25000000, alias="MAX_FILE_BYTES_SIZE"
    )
    token_exp_minutes: float = Field(default=60, alias="TOKEN_EXPIRE_MINUTES")
    jwt_secret_key: Optional[str] = Field(default="secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: Optional[str] = Field(default="HS256", alias="JWT_ALGORITHM")
    gcp_creds: str = Field(default=..., alias="GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name: Optional[str] = Field(default="new-bucket", alias="BUCKET_NAME")
    gcp_storage_exp_minutes: float = Field(default=15, alias="STORAGE_EXPIRE_MINUTES")
    pinecone_api_key: str = Field(default=..., alias="PINECONE_API_KEY")
    pinecone_index_name: Optional[str] = Field(
        default="ai-file-search-service-index", alias="PINECONE_INDEX_NAME"
    )
    openai_api_key: str = Field(default=..., alias="OPENAI_API_KEY")
    embedding_chunk_size: Optional[int] = Field(
        default=200, alias="EMBEDDING_CHUNK_SIZE"
    )
    embedding_namespace: Optional[str] = Field(
        default="paragraphs", alias="EMBEDDING_NAMESPACE"
    )
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_cache_db: Optional[int] = Field(default=1, alias="REDIS_CACHE_DB")
    redis_cache_exp: Optional[int] = Field(default=86400, alias="REDIS_CACHE_EXP")

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.gcp_creds
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    return settings
