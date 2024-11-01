from celery import shared_task
from langchain_core.exceptions import LangChainException
from loguru import logger

from dependencies import get_llm_embedding_client, get_pinecone_index
from jobs.job1.utils import format_pinecone_payload
from settings import get_settings

settings = get_settings()
embedding_client = get_llm_embedding_client(settings)
pinecone_index = get_pinecone_index(settings)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="jobs.job1:add",
)
def add(self, x, y):
    import time

    time.sleep(30)
    print(self)
    return x + y


@shared_task(
    bind=True,
    autoretry_for=(LangChainException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="jobs.job1:embed_save_job",
)
def embed_save_job(self, extracted_texts: list[str], filename: str):
    """
    Embeds the extracted texts and save it to a pinecone vector database asynchronously.

    Generating fake embeddings
        from langchain_community.embeddings import FakeEmbeddings
        embeddings = FakeEmbeddings(size=1536)
        embeddings = embeddings.embed_documents(extracted_texts)

    :param extracted_texts: list of extracted texts type list[str]
    :param filename: filename
    :return: None
    """
    try:
        logger.info("Embedding extracted texts...")
        embeddings = embedding_client.embed_documents(extracted_texts)
    except LangChainException as exc:
        logger.error("Exception while embedding extracted texts: %s", exc)
        return

    index_payload = format_pinecone_payload(extracted_texts, embeddings, filename)
    logger.info("Upserting to database")
    response = pinecone_index.upsert(
        vectors=index_payload,
        namespace=settings.embedding_namespace,
        batch_size=settings.embedding_chunk_size,
    )
    logger.info("Waiting for async task results...")
    logger.info(response.upserted_count)
    logger.info("Done processing")

    return response.upserted_count
