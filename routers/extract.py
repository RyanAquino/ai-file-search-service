"""Extract API endpoint module."""

from fastapi import APIRouter, Depends

from dependencies import (
    get_current_user,
    get_llm_embedding_client,
    get_pinecone_index,
    get_redis_client,
)
from models.response import BaseDataResponse
from operations.semantic_search_service import SemanticSearchService
from settings import Settings, get_settings

router = APIRouter()


@router.post("/extract")
def extract_related_words(
    query_text: str,
    file_id: str,
    settings: Settings = Depends(get_settings),
    _=Depends(get_current_user),
    pinecone_index=Depends(get_pinecone_index),
    llm_embedding_client=Depends(get_llm_embedding_client),
    redis_client=Depends(get_redis_client),
) -> BaseDataResponse:
    """
    Extract related words based on given File ID and query text.

    :param _: Auth dependency
    :param query_text: Search query text
    :param file_id: File ID or file name
    :param settings: Application settings dependency
    :param pinecone_index: Pinecone index dependency
    :param llm_embedding_client: OpenAI llm embedding client dependency
    :param redis_client: Redis client dependency
    :return: BaseDataResponse - list of extracted paragraphs related to search term
    """
    search_service = SemanticSearchService(
        settings, pinecone_index, llm_embedding_client, redis_client
    )
    match_texts = search_service.search(query_text, file_id)

    return BaseDataResponse(data=match_texts)
