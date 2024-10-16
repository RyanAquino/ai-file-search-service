"""OCR API Endpoint module."""

from fastapi import APIRouter, Depends, Request, Response, status

from dependencies import get_current_user, get_llm_embedding_client, get_pinecone_index, get_redis_rq_client
from models.requests import OCRRequestURLs
from operations.ocr_service import OCRService
from rate_limit_config import limiter
from settings import Settings, get_settings

router = APIRouter()


@router.post("/ocr", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
@limiter.limit("10/hour")
async def process_ocr(
    request: Request,
    payload: OCRRequestURLs,
    settings: Settings = Depends(get_settings),
    _=Depends(get_current_user),
    pinecone_index=Depends(get_pinecone_index),
    llm_embedding_client=Depends(get_llm_embedding_client),
    task_queue = Depends(get_redis_rq_client),
):
    """
    A mock OCR endpoint that processes OCR results
    embeds texts and saves it to Pinecone vector database.

    :param request: Request object required for rate limiting
    :param payload: payload of type OCRRequestURLs
    :param settings: Application settings dependency
    :param _: Auth dependency
    :param pinecone_index: Pinecone index dependency
    :param llm_embedding_client: OpenAI llm embedding client dependency
    :return:
    """
    ocr_service = OCRService(
        settings, payload.url, pinecone_index, llm_embedding_client, task_queue
    )
    await ocr_service.process_url()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
