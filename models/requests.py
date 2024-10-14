"""API Requests module."""

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """User register request model."""

    username: str = Field(default=..., description="Username")
    password: str = Field(default=..., description="Password")


class OCRRequestURLs(BaseModel):
    """OCR API request URLs model."""

    urls: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "urls": [
                        "https://storage.googleapis.com/ai-file-search-service_new-bucket/"
                        "建築基準法施行令.json?"
                        "Expires=1728795108",
                    ]
                }
            ]
        }
    }
