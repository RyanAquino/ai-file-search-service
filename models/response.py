from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UserToken(BaseModel):
    exp: datetime
    sub: str | Column[str]
    iat: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserRegisterResponse(BaseModel):
    id: int
    username: str


class BaseDataResponse(BaseModel):
    data: Optional[list]
