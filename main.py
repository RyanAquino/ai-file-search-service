import uvicorn
import os
from fastapi import FastAPI
from routers import router
from settings import get_settings


def create_app():
    app = FastAPI()
    app.include_router(router.api_router)
    return app


def main():
    app = create_app()
    settings = get_settings()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.gcp_creds
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )


if __name__ == "__main__":
    main()
