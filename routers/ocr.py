from fastapi import APIRouter

router = APIRouter()


@router.post("/ocr")
def process_ocr():
    return [{"username": "Rick"}, {"username": "Morty"}]
