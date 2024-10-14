"""Rate limit config module."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from settings import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    in_memory_fallback_enabled=True,
)
