"""Main module."""

import uvicorn
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from rate_limit_config import limiter
from routers import router
from settings import get_settings


def create_app(disable_limiter=False):
    """
    Create FatAPI application.

    :param disable_limiter: Boolean value to enable/disable rate limiting.
    :return: FastAPI application instance.
    """
    app = FastAPI()

    if disable_limiter:
        limiter.enabled = False

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.include_router(router.api_router)
    return app


def main():
    """Main entry point for FastAPI application."""
    app = create_app()
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )


if __name__ == "__main__":
    main()
