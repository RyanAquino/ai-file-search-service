import uuid
from datetime import timedelta

from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError

from settings import Settings
from werkzeug.utils import secure_filename
from google.cloud import storage


class FileProcessor:

    def __init__(self, app_settings: Settings, gcp_client: storage.Client, files: list[UploadFile]):
        self.files = files
        self.settings = app_settings
        self.gcp_client = gcp_client
        self.bucket = self.gcp_client.bucket(f"{self.gcp_client.project}_{self.settings.bucket_name}")

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
                {
                    "filename": file.filename,
                    "sanitized_filename": f"{uuid.uuid4()}_{secure_filename(file.filename)}",
                    "file_obj": file,
                }
            )

        return sanitized_files

    def generate_signed_url(self, file_name: str):
        blob = self.bucket.blob(file_name)
        expiration_time = timedelta(minutes=self.settings.gcp_storage_exp_minutes)
        signed_url = blob.generate_signed_url(expiration=expiration_time)

        return signed_url

    def upload_files(self):
        files = self.sanitize_file_names()
        presigned_urls = []

        for file in files:
            file_obj = file.get("file_obj")
            sanitized_name = file.get("sanitized_filename")
            
            blob = self.bucket.blob(sanitized_name)
            blob.upload_from_file(file_obj.file, content_type=file_obj.content_type)
            
            presigned_url = self.generate_signed_url(sanitized_name)
            presigned_urls.append({
                "filename": file.get("filename"),
                "presigned_url": presigned_url,
            })

        return presigned_urls
