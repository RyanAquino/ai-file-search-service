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
    search_service = SemanticSearchService(
        settings, pinecone_index, llm_embedding_client, redis_client
    )
    match_texts = search_service.search(query_text, file_id)

    return BaseDataResponse(data=match_texts)
