from fastapi import APIRouter, Depends, Request, Response, status

from dependencies import get_current_user, get_llm_embedding_client, get_pinecone_index
from operations.ocr_service import OCRService
from rate_limit_config import limiter
from settings import Settings, get_settings

router = APIRouter()


@router.post("/ocr", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
@limiter.limit("10/hour")
async def process_ocr(
    request: Request,
    urls: list[str],
    settings: Settings = Depends(get_settings),
    _=Depends(get_current_user),
    pinecone_index=Depends(get_pinecone_index),
    llm_embedding_client=Depends(get_llm_embedding_client),
):
    ocr_service = OCRService(settings, urls, pinecone_index, llm_embedding_client)
    await ocr_service.process_urls()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
