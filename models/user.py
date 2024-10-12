"""User Model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base SQLAlchemy ORM."""


class User(Base):
    """Database model for users"""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100), nullable=False)
