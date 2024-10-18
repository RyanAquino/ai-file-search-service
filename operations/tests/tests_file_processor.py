"""Test FileProcessor module."""

import os

from fastapi import UploadFile

from conftest import override_gcp_client, override_get_settings
from operations.file_processor import FileProcessor


def test_sanitize_file_names(tmp_path):
    """
    Test sanitize file name.

    :param tmp_path: temporary path fixture
    """
    temp_filename = "hello.txt"
    with open(os.path.join(tmp_path, temp_filename), "wb") as file:
        file.write(b"test content")

        file_processor = FileProcessor(
            override_get_settings(),
            override_gcp_client(),
            files=[UploadFile(file=file, filename=temp_filename)],
        )
        result = file_processor.sanitize_file_names()
        assert result and len(result) == 1
