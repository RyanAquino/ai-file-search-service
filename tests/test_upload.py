"""Test Upload API module."""

import pytest

from settings import get_settings


class TestUploadAPI:
    """Test Upload API class."""

    def test_upload_invalid_file_type(self, login_client, tmp_path):
        """
        Test upload invalid file type.

        :param login_client: fixture of logged in client
        :param tmp_path: builtin temporary file path fixture
        """
        test_client, _ = login_client

        pdf_path = tmp_path / "sample.txt"

        with open(pdf_path, "wb") as f:
            f.write(b"Sample PDF File!")

        with open(pdf_path, "rb") as f:
            files = [
                (
                    "files",
                    ("sample.txt", f, "text/plain"),
                ),
            ]
            response = test_client.post("/api/v1/upload", files=files)
            assert response.status_code == 400
            assert "detail" in response.json()

    def test_upload_invalid_more_than_max_upload_count(self, login_client, tmp_path):
        """
        Test upload invalid more_than_max_upload_count of 5.

        :param login_client: fixture of logged in client
        :param tmp_path: builtin temporary file path fixture
        """
        test_client, app = login_client

        def override_settings():
            class MockSettings:
                bucket_name = "test-bucket"
                max_file_upload_count = 5

            return MockSettings()

        app.dependency_overrides[get_settings] = override_settings

        files = [
            (
                "files",
                ("sample1.txt", b""),
            ),
            (
                "files",
                ("sample2.txt", b""),
            ),
            (
                "files",
                ("sample3.txt", b""),
            ),
            (
                "files",
                ("sample4.txt", b""),
            ),
            (
                "files",
                ("sample5.txt", b""),
            ),
            (
                "files",
                ("exceeded.txt", b""),
            ),
        ]
        response = test_client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert response.json() == {"detail": "Maximum number of valid files: 5"}

    def test_upload_invalid_no_file_extension(self, login_client):
        """
        Test upload no file extension.

        :param login_client: fixture of logged in client
        """
        test_client, _ = login_client

        files = [
            (
                "files",
                ("no-file-extension", b""),
            ),
        ]
        response = test_client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Invalid file no extension: no-file-extension"
        }

    def test_upload_invalid_exceed_max_file_size(self, login_client):
        """
        Test upload exceed max_file_size exceeded.

        :param login_client: fixture of logged in client
        """
        test_client, app = login_client

        def override_settings():
            class MockSettings:
                bucket_name = "test-bucket"
                max_file_bytes_size = 1
                max_file_upload_count = 5

            return MockSettings()

        app.dependency_overrides[get_settings] = override_settings

        files = [
            (
                "files",
                ("sample-bytes.pdf", b"testing 123", "application/pdf"),
            ),
        ]
        response = test_client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert response.json() == {
            "detail": "File size too large for file sample-bytes.pdf"
        }

    @pytest.mark.parametrize(
        "test_input,expected_count",
        [
            # Single file upload
            (
                [
                    (
                        "files",
                        ("sample-bytes.pdf", b"testing 123", "application/pdf"),
                    ),
                ],
                1,
            ),
            # Multiple file upload
            (
                [
                    (
                        "files",
                        ("sample-bytes1.pdf", b"testing 123", "application/pdf"),
                    ),
                    (
                        "files",
                        ("sample-bytes2.pdf", b"testing 123", "application/pdf"),
                    ),
                ],
                2,
            ),
        ],
    )
    def test_upload_valid_files(self, test_input, expected_count, login_client):
        """
        Test upload valid files.

        :param test_input: parametrize inputs of different scenarios
        :param expected_count: parametrize expected output for each scenario
        :param login_client: fixture of logged in client
        """
        test_client, _ = login_client
        response = test_client.post("/api/v1/upload", files=test_input)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data is not None
        assert len(response_data.get("data", [])) == expected_count
