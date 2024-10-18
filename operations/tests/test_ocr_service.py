"""Test OCR module."""

from conftest import (
    override_get_llm_embedding_client,
    override_get_pinecone_index,
    override_get_settings,
)
from operations.ocr_service import OCRService


class TestOCRService:
    """Test OCRService operations class."""

    def test_get_ocr_texts_results(self):
        """Test OCRService get_ocr_texts_results function."""
        ocr_service = OCRService(
            override_get_settings(),
            "sample-url",
            override_get_pinecone_index(),
            override_get_llm_embedding_client(),
        )
        sample_results = {"paragraphs": [{"content": "Sample text"}]}
        result = ocr_service.get_ocr_texts_results(sample_results)
        assert result and len(result) == 1

    def test_format_pinecone_payload(self):
        """Test format_pinecone_payload function."""
        ocr_service = OCRService(
            override_get_settings(),
            "sample-url",
            override_get_pinecone_index(),
            override_get_llm_embedding_client(),
        )

        response = ocr_service.format_pinecone_payload(
            ["Sample text"], [1, 2, 3], "test file name"
        )

        assert response and len(response) == 1
