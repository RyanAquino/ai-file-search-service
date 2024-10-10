from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError

from settings import Settings


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
            file_ext = file.filename.split(".")

            if not file_ext:
                raise RequestValidationError(f"Invalid file no extension: {file.filename}")

            file_ext = file_ext[-1]

            if file.content_type not in valid_content_types or file_ext not in valid_extensions:
                raise RequestValidationError(f"Valid types supported: {valid_file_types}")

            if file.size > self.settings.max_file_bytes_size:
                raise RequestValidationError(f"File size too large for file {file.filename}")

    def process_upload(self):
        pass
