from fastapi import APIRouter

from routers import auth, extract, ocr, upload

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(extract.router)
api_router.include_router(ocr.router)
api_router.include_router(upload.router)
api_router.include_router(auth.router)
