"""Main module."""

import uvicorn
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from celery_app import init_celery
from rate_limit_config import limiter
from routers import router
from settings import get_settings

settings = get_settings()


def create_app(disable_limiter=False):
    """
    Create FastAPI application.

    :param disable_limiter: Boolean value to enable/disable rate limiting.
    :return: FastAPI application instance.
    """
    app = FastAPI(
        title="AI File Search Service",
        description="AI File Search Service",
        version="1.0.0",
    )

    if disable_limiter:
        limiter.enabled = False

    app.state.limiter = limiter
    app.celery = init_celery(settings)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.include_router(router.api_router)
    return app


app = create_app()
celery = app.celery


def main():
    """Main entry point for FastAPI application."""
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        workers=settings.app_workers,
    )


if __name__ == "__main__":
    main()
