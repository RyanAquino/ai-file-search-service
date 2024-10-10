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

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
