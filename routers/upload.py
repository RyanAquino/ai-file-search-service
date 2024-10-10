
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.exceptions import RequestValidationError

from operations.file_processor import FileProcessor
from settings import Settings, get_settings

router = APIRouter()


@router.post("/upload")
def upload_attachments(files: list[UploadFile], settings: Settings = Depends(get_settings)):
    process = FileProcessor(settings, files)

    try:
        process.validate_files()
    except RequestValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    process.upload_files()

    return [{"username": "Rick"}, {"username": "Morty"}]
