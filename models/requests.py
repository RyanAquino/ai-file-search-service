"""API Requests module."""

from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """User register request model."""

    username: str = Field(default=..., description="Username")
    password: str = Field(default=..., description="Password")


class OCRRequestURLs(BaseModel):
    """OCR API request URLs model."""

    url: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://storage.googleapis.com/ai-file-search-service_new-bucket/"
                    "建築基準法施行令.json?"
                    f"Expires={(datetime.now() + timedelta(days=5)).timestamp()}",
                }
            ]
        }
    }
