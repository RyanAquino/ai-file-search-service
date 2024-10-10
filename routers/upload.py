from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
def upload_attachments():
    return [{"username": "Rick"}, {"username": "Morty"}]
