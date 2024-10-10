from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UserToken(BaseModel):
    exp: datetime
    sub: str
    iat: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
