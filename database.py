"""Database module."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.user import Base
from settings import get_settings

settings = get_settings()
engine = create_engine(settings.db_url, pool_pre_ping=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """
    Retrieve database session.

    :yield: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
