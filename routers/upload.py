
from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from google.cloud import storage

from dependencies import get_current_user, get_gcp_client
from operations.file_processor import FileProcessor
from settings import Settings, get_settings

router = APIRouter()


@router.post("/upload")
def upload_attachments(
    files: list[UploadFile],
    settings: Settings = Depends(get_settings),
    gcp_client: storage.Client = Depends(get_gcp_client),
    _=Depends(get_current_user),
):
    process = FileProcessor(settings, gcp_client, files)

    try:
        process.validate_files()
    except RequestValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    urls = process.upload_files()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": urls})
