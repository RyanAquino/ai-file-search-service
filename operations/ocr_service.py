"""OCR Service module."""

import json
import time
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from pinecone import Pinecone

from settings import Settings


class OCRService:
    """OCR Service class."""

    def __init__(
        self,
        settings: Settings,
        urls: list[str],
        pinecone_index: Pinecone.Index,
        embedding_client: OpenAIEmbeddings,
    ):
        """
        Inject class dependencies.

        :param settings: Application settings
        :param urls: request payload URLs
        :param pinecone_index: Pinecone index dependency
        :param embedding_client: OpenAI embedding dependency
        """
        self.urls = urls
        self.settings = settings
        self.embedding_client = embedding_client
        self.pinecone_index = pinecone_index

    @staticmethod
    def process_ocr(filename: str) -> dict:
        """
        Mock processing of OCR

        :param filename: filename to be processed
        :return: OCR result from mock `ocr` directory
        """
        logger.info("Processing OCR...")

        ocr_path = Path("ocr", filename)

        if not ocr_path.exists():
            logger.error(f"OCR file {filename} does not exist!")
            return {}

        with open(ocr_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            ocr_results = data.get("analyzeResult")

        return ocr_results

    async def process_urls(self):
        """
        OCR API that processes request payload URLs embeddings asynchronously.

        :return: None
        """
        texts = []
        text_file_mappings = {}

        for url in self.urls:
            filename = self.get_filename_from_url(url)
            ocr_result = self.process_ocr(filename)

            if not ocr_result:
                logger.warning(f"No OCR Results found for file: {filename}")
                continue

            for paragraph in ocr_result.get("paragraphs", []):
                paragraph_text = paragraph.get("content")
                texts.append(paragraph_text)
                text_file_mappings[paragraph_text] = filename

        if not texts:
            logger.error("No texts extracted from files")
            raise HTTPException(status_code=400, detail="Failed to process OCR")

        embeddings = await self.embedding_client.aembed_documents(texts)

        index_payload = []
        for txt, embedding in zip(texts, embeddings):

            file_id = text_file_mappings.get(txt)
            if not file_id:
                logger.warning(f"Text {txt} not found on any file")
                continue

            index_payload.append(
                {
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": {"text": txt, "file_id": file_id},
                }
            )

        for idx in range(0, len(index_payload), self.settings.embedding_chunk_size):
            self.pinecone_index.upsert(
                vectors=index_payload[
                    idx : idx + self.settings.embedding_chunk_size - 1
                ],
                namespace=self.settings.embedding_namespace,
                async_req=True,
            )

    def get_filename_from_url(self, signed_url: str) -> str:
        """
        Validate and get filename from presigned URL.

        :param signed_url: presigned URL
        :return: URL
        """
        parsed_url = urlparse(signed_url)

        if not signed_url.startswith("https"):
            raise RequestValidationError(
                "Signed URL must use HTTPS for secure transmission."
            )

        if not parsed_url.netloc.endswith("storage.googleapis.com"):
            raise RequestValidationError("Invalid signed URL: must be for GCS")

        if self.settings.bucket_name not in parsed_url.path:
            raise RequestValidationError(
                f"Signed URL not pointing to expected bucket {self.settings.bucket_name}"
            )

        expire_time = parse_qs(parsed_url.query).get("Expires")

        if not expire_time or float(expire_time[0]) <= time.time():
            raise RequestValidationError("Invalid signed URL: expired")

        return parsed_url.path.split("/")[-1]
