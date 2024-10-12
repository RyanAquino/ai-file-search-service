"""API Requests module."""

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """User register request model."""

    username: str = Field(default=..., description="Username")
    password: str = Field(default=..., description="Password")
