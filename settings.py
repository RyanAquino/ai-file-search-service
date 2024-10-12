import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = Field(default="0.0.0.0", alias='APP_HOST')
    app_port: int = Field(3000, alias='APP_PORT')
    app_debug: bool = Field(False, alias='APP_DEBUG')
    db_url: str = Field(..., alias='DB_URL')
    max_file_upload_count: int = Field(default=5, alias='MAX_FILE_UPLOAD_COUNT')
    max_file_bytes_size: int = Field(default=25000000, alias='MAX_FILE_BYTES_SIZE')
    token_exp_minutes: int = Field(default=60, alias='TOKEN_EXPIRE_MINUTES')
    jwt_secret_key: str = Field("secret-key", alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field("HS256", alias='JWT_ALGORITHM')
    gcp_creds: str = Field(..., alias='GOOGLE_APPLICATION_CREDENTIALS')
    bucket_name: str = Field(default="new-bucket", alias='BUCKET_NAME')
    gcp_storage_exp_minutes: int = Field(default=15, alias='STORAGE_EXPIRE_MINUTES')
    pinecone_api_key: str = Field(..., alias='PINECONE_API_KEY')
    pinecone_index_name: str = Field("ai-file-search-service-index", alias='PINECONE_INDEX_NAME')
    openai_api_key: str = Field(..., alias='OPENAI_API_KEY')
    embedding_chunk_size: int = Field(default=200, alias='EMBEDDING_CHUNK_SIZE')
    embedding_namespace: str = Field(default="paragraphs", alias='EMBEDDING_NAMESPACE')
    redis_host: str = Field("localhost", alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')
    redis_cache_db: int = Field(1, alias='REDIS_CACHE_DB')

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.gcp_creds
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    return settings
