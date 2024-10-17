"""API Requests module."""

from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """User register request model."""

    username: str = Field(default=..., description="Username")
    password: str = Field(default=..., description="Password")


class ExtractRequest(BaseModel):
    """Extract API request model."""

    query_text: str = Field(default=..., description="Query texts")
    file_id: str = Field(default=..., description="File id")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query_text": "building, floors and walls",
                    "file_id": "東京都建築安全条例.json",
                }
            ]
        }
    }


class OCRRequestURLs(BaseModel):
    """OCR API request URLs model."""

    url: str = Field(default=..., description="File URL")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://storage.googleapis.com/ai-file-search-service_new-bucket/"
                    "東京都建築安全条例.json"
                    f"?Expires={int((datetime.now() + timedelta(days=5)).timestamp())}",
                }
            ]
        }
    }
