"""Test OCR API module."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest


class TestOCREmbeddingsAPI:
    """Test OCR API class."""

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (
                {"url": "http://test-url-input"},
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
            (
                {"url": "some random text only"},
                {"detail": "Given URL is not a valid URL."},
            ),
        ],
    )
    def test_invalid_filename_urls(self, test_input, expected, login_client):
        """
        Test invalid filename scenarios.

        :param test_input: parametrize test input
        :param expected: parametrize test expected output
        :param login_client: login client fixture
        """
        test_client, _ = login_client

        response = test_client.post("api/v1/ocr", json=test_input)

        assert response.status_code == 422
        assert response.json() == expected

    @patch(
        "operations.ocr_service.OCRService.process_ocr",
        lambda *args: {"paragraphs": [{"content": ""}]},
    )
    def test_no_texts_extracted(self, login_client):
        """
        Tests no text extracted from a mock file.

        :param login_client: login client fixture
        """
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
    @patch("fastapi.background.BackgroundTasks.add_task")
    def test_valid_texts_extracted_and_saved(self, add_task_mock, login_client):
        """
        Tests valid input with text extracted from a mock file.

        :param login_client: login client fixture
        """
        add_task_mock.return_value = lambda *args: None

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
        assert add_task_mock.call_count == 1
