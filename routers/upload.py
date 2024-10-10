
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.exceptions import RequestValidationError

from dependencies import get_current_user
from operations.file_processor import FileProcessor
from settings import Settings, get_settings

router = APIRouter()


@router.post("/upload")
def upload_attachments(
    files: list[UploadFile],
    settings: Settings = Depends(get_settings),
    _=Depends(get_current_user),
):
    process = FileProcessor(settings, files)

    try:
        process.validate_files()
    except RequestValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    process.process_upload()

    return [{"username": "Rick"}, {"username": "Morty"}]
