"""User Model."""

import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base SQLAlchemy ORM."""


class User(Base):
    """Database model for users"""

    __tablename__ = "user"

    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100), nullable=False)
