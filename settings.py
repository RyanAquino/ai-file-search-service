from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = Field(default="0.0.0.0", alias='APP_HOST')
    app_port: int = Field(3000, alias='APP_PORT')
    app_debug: bool = Field(False, alias='APP_DEBUG')

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
