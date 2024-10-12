from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    username: str = Field(default=..., description="Username")
    password: str = Field(default=..., description="Password")
