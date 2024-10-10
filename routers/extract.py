from fastapi import APIRouter

router = APIRouter()


@router.post("/extract")
def extract_related_words():
    return [{"username": "Rick"}, {"username": "Morty"}]
