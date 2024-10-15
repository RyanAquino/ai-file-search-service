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
        url: str,
        pinecone_index: Pinecone.Index,
        embedding_client: OpenAIEmbeddings,
    ):
        """
        Inject class dependencies.

        :param settings: Application settings
        :param url: request payload URL to be processed
        :param pinecone_index: Pinecone index dependency
        :param embedding_client: OpenAI embedding dependency
        """
        self.url = url
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

    @staticmethod
    def get_ocr_texts_results(ocr_result: dict) -> list[str]:
        """
        Retrieve OCR texts results from response.

        :param ocr_result: OCR result from `ocr` directory
        :return: list of texts
        """
        texts = []

        for paragraph in ocr_result.get("paragraphs", []):
            paragraph_text = paragraph.get("content")
            if paragraph_text:
                texts.append(paragraph_text)

        return texts

    @staticmethod
    def format_pinecone_payload(extracted_texts, embeddings, filename) -> list[dict]:
        """
        Formats th tests with its embeddings and metadata.

        :param extracted_texts: list of extracted texts type list[str]
        :param embeddings: list of embeddings
        :param filename: filename as file_id
        :return: list of objects ready for pinecone upsert
        """
        index_payload = []
        for txt, embedding in zip(extracted_texts, embeddings):
            index_payload.append(
                {
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": {"text": txt, "file_id": filename},
                }
            )

        return index_payload

    async def process_url(self):
        """
        OCR API that processes request payload URLs embeddings asynchronously.

        :return: None
        """
        filename = self.get_filename_from_url(self.url)
        ocr_result = self.process_ocr(filename)

        if not ocr_result:
            logger.warning(f"No OCR Results found for file: {filename}")
            raise HTTPException(
                status_code=404, detail="No OCR Results found for given file"
            )

        extracted_texts = self.get_ocr_texts_results(ocr_result)

        if not extracted_texts:
            logger.error("No texts extracted from file")
            raise HTTPException(status_code=400, detail="No texts extracted from file.")

        embeddings = await self.embedding_client.aembed_documents(extracted_texts)
        index_payload = self.format_pinecone_payload(
            extracted_texts, embeddings, filename
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

        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise RequestValidationError("Given URL is not a valid URL.")

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
