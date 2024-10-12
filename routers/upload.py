from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.exceptions import RequestValidationError
from google.cloud import exceptions, storage  # type: ignore[attr-defined]

from dependencies import get_current_user, get_gcp_client
from models.response import BaseDataResponse
from operations.file_processor import FileProcessor
from settings import Settings, get_settings

router = APIRouter()


@router.post("/upload")
def upload_attachments(
    files: list[UploadFile],
    settings: Settings = Depends(get_settings),
    gcp_client: storage.Client = Depends(get_gcp_client),
    _=Depends(get_current_user),
) -> BaseDataResponse:
    process = FileProcessor(settings, gcp_client, files)

    try:
        process.validate_files()
    except RequestValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())

    try:
        urls = process.upload_files()
    except exceptions.GoogleCloudError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.errors()
        )

    return BaseDataResponse(data=urls)
