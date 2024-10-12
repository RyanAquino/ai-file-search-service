"""File processor module."""

import uuid
from datetime import timedelta

from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError
from google.cloud import exceptions, storage  # type: ignore[attr-defined]
from werkzeug.utils import secure_filename

from settings import Settings


class FileProcessor:
    """File processor class."""

    def __init__(
        self,
        app_settings: Settings,
        gcp_client: storage.Client,
        files: list[UploadFile],
    ):
        """
        Inject class dependencies.

        :param app_settings: Application Settings
        :param gcp_client: GCP Client
        :param files: request payload input files
        """
        self.files = files
        self.settings = app_settings
        self.gcp_client = gcp_client
        self.bucket = self.gcp_client.bucket(
            f"{self.gcp_client.project}_{self.settings.bucket_name}"
        )

    def validate_files(self):
        """
        Validate files uploaded from the request payload.
        :raises: RequestValidationError
        """
        if len(self.files) > self.settings.max_file_upload_count:
            raise RequestValidationError(
                f"Maximum number of valid files: {self.settings.max_file_upload_count}"
            )

        valid_content_types = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff",
            "application/pdf",
        }
        valid_extensions = [
            content_type.split("/")[-1] for content_type in valid_content_types
        ]
        valid_file_types = ", ".join(valid_extensions)

        for file in self.files:
            if "." not in file.filename:
                raise RequestValidationError(
                    f"Invalid file no extension: {file.filename}"
                )

            file_ext = file.filename.split(".")[-1]

            if (
                file.content_type.lower() not in valid_content_types
                or file_ext.lower() not in valid_extensions
            ):
                raise RequestValidationError(
                    f"Valid types supported: {valid_file_types}"
                )

            if file.size > self.settings.max_file_bytes_size:
                raise RequestValidationError(
                    f"File size too large for file {file.filename}"
                )

    def sanitize_file_names(self) -> list[dict]:
        """
        Sanitize file names before uploading to cloud storage.

        :return: list of sanitized file names
        """
        sanitized_files = []

        for file in self.files:

            if not file.filename:
                continue

            sanitized_files.append(
                {
                    "filename": file.filename,
                    "sanitized_filename": f"{uuid.uuid4()}_{secure_filename(file.filename)}",
                    "file_obj": file,
                }
            )

        return sanitized_files

    def generate_signed_url(self, file_name: str) -> str:
        """
        Helper function to generate signed URL from a file.

        :param file_name: File name
        :return: signed URL
        """
        blob = self.bucket.blob(file_name)
        expiration_time = timedelta(minutes=self.settings.gcp_storage_exp_minutes)
        signed_url = blob.generate_signed_url(expiration=expiration_time)

        return signed_url

    def upload_files(self) -> list[dict]:
        """
        Upload files to cloud storage.

        :return: list of uploaded files with sanitized filename and presigned URL
        """
        files = self.sanitize_file_names()
        presigned_urls = []

        for file in files:
            file_obj = file.get("file_obj")
            sanitized_name = file.get("sanitized_filename")

            if not file_obj or not sanitized_name:
                continue

            try:
                blob = self.bucket.blob(sanitized_name)
                blob.upload_from_file(file_obj.file, content_type=file_obj.content_type)
                presigned_url = self.generate_signed_url(sanitized_name)
            except exceptions.GoogleCloudError as exc:
                raise exc

            presigned_urls.append(
                {
                    "filename": file.get("filename"),
                    "file_id": sanitized_name,
                    "presigned_url": presigned_url,
                }
            )

        return presigned_urls
