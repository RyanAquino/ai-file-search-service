from datetime import datetime, timedelta
from unittest.mock import patch

import pytest


class TestOCREmbeddingsAPI:

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (
                {"url": "test-url-input"},
                {"detail": "Signed URL must use HTTPS for secure transmission."},
            ),
            (
                {"url": "https://non-googleapi.com/bucket/file.txt"},
                {"detail": "Invalid signed URL: must be for GCS"},
            ),
            (
                {"url": "https://storage.googleapis.com/non-existent-bucket/file.txt"},
                {"detail": "Signed URL not pointing to expected bucket test-bucket"},
            ),
            (
                {
                    "url": "https://storage.googleapis.com/test-bucket/file.txt?Expires=1"
                },
                {"detail": "Invalid signed URL: expired"},
            ),
        ],
    )
    def test_invalid_filename_urls(self, test_input, expected, login_client):
        test_client, _ = login_client

        response = test_client.post("api/v1/ocr", json=test_input)

        assert response.status_code == 422
        assert response.json() == expected

    @patch(
        "operations.ocr_service.OCRService.process_ocr",
        lambda *args: {"paragraphs": [{"content": ""}]},
    )
    def test_no_texts_extracted(self, login_client):
        test_client, _ = login_client

        future_ts = (datetime.now() + timedelta(days=1)).timestamp()
        response = test_client.post(
            "api/v1/ocr",
            json={
                "url": f"https://storage.googleapis.com/test-bucket/file.txt?Expires={future_ts}"
            },
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "No texts extracted from file."}

    @patch(
        "operations.ocr_service.OCRService.process_ocr",
        lambda *args: {"paragraphs": [{"content": "Sample paragraph content!"}]},
    )
    def test_valid_texts_extracted_and_saved(self, login_client):
        test_client, _ = login_client

        future_ts = (datetime.now() + timedelta(days=1)).timestamp()
        response = test_client.post(
            "api/v1/ocr",
            json={
                "url": f"https://storage.googleapis.com/test-bucket/file.txt?Expires={future_ts}"
            },
        )
        assert response.status_code == 204
        assert response.content == b""
