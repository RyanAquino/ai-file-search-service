"""API Requests module."""

from pydantic import BaseModel, Field, RootModel


class UserRegisterRequest(BaseModel):
    """User register request model."""

    username: str = Field(default=..., description="Username")
    password: str = Field(default=..., description="Password")


class OCRRequestURLs(RootModel):
    """OCR API request URLs model."""

    root: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [
                [
                    "https://storage.googleapis.com/ai-file-search-service_new-bucket/"
                    "建築基準法施行令.json?"
                    "Expires=1728795108",
                ]
            ]
        }
    }
