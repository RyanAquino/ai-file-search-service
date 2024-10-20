"""Settings module."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_host: Optional[str] = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: Optional[int] = Field(default=3000, alias="APP_PORT")
    app_debug: Optional[bool] = Field(default=False, alias="APP_DEBUG")
    app_workers: Optional[int] = Field(default=1, alias="APP_WORKERS")
    db_url: str = Field(default="db", alias="DB_URL")
    max_file_upload_count: Optional[int] = Field(
        default=5, alias="MAX_FILE_UPLOAD_COUNT"
    )
    max_file_bytes_size: Optional[int] = Field(
        default=25000000, alias="MAX_FILE_BYTES_SIZE"
    )
    token_exp_minutes: float = Field(default=60, alias="TOKEN_EXPIRE_MINUTES")
    jwt_secret_key: Optional[str] = Field(default="secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: Optional[str] = Field(default="HS256", alias="JWT_ALGORITHM")
    gcp_creds: str = Field(
        default="credentials.json", alias="GOOGLE_APPLICATION_CREDENTIALS"
    )
    bucket_name: str = Field(default="new-bucket", alias="BUCKET_NAME")
    gcp_storage_exp_minutes: float = Field(default=15, alias="STORAGE_EXPIRE_MINUTES")
    pinecone_api_key: str = Field(default="key", alias="PINECONE_API_KEY")
    pinecone_host: str = Field(default="host", alias="PINECONE_HOST")
    pinecone_pool_count: int = Field(default=1, alias="PINECONE_POOL_COUNT")
    openai_api_key: str = Field(default="key", alias="OPENAI_API_KEY")
    openai_embeddings_dimensions: Optional[int] = Field(
        default=None, alias="OPENAI_EMBEDDINGS_DIMENSIONS"
    )
    openai_embeddings_model: str = Field(
        default="text-embedding-ada-002", alias="OPENAI_EMBEDDING_MODEL"
    )
    embedding_chunk_size: int = Field(default=200, alias="EMBEDDING_CHUNK_SIZE")
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
    """Get application settings and set needed env variables."""
    settings = Settings()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.gcp_creds
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    return settings
