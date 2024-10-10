import uuid

from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError

from settings import Settings
from werkzeug.utils import secure_filename


class FileProcessor:

    def __init__(self, settings: Settings, files: list[UploadFile]):
        self.files = files
        self.settings = settings

    def validate_files(self):
        if len(self.files) > self.settings.max_file_upload_count:
            raise RequestValidationError(f"Maximum number of valid files: {self.settings.max_file_upload_count}")

        valid_content_types = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff",
            "application/pdf"
        }
        valid_extensions = [content_type.split("/")[-1] for content_type in valid_content_types]
        valid_file_types = ', '.join(valid_extensions)

        for file in self.files:
            if "." not in file.filename:
                raise RequestValidationError(f"Invalid file no extension: {file.filename}")

            file_ext = file.filename.split(".")[-1]

            if file.content_type.lower() not in valid_content_types or file_ext.lower() not in valid_extensions:
                raise RequestValidationError(f"Valid types supported: {valid_file_types}")

            if file.size > self.settings.max_file_bytes_size:
                raise RequestValidationError(f"File size too large for file {file.filename}")

    def sanitize_file_names(self):
        sanitized_files = []

        for file in self.files:
            sanitized_files.append(
                f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            )

        return sanitized_files

    def upload_files(self):
        files = self.sanitize_file_names()
        # Upload
        # Get signed URLs

