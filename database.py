"""Database module."""

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.user import Base
from settings import Settings, get_settings


def session_factory(settings: Settings = Depends(get_settings)):
    """
    Database session factory dependency.

    :param settings: Application settings dependency
    :return: session factory
    """
    engine = create_engine(settings.db_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session(session: sessionmaker = Depends(session_factory)):
    """
    Retrieve database session.

    :yield: Database session
    """
    db = session()
    try:
        yield db
    finally:
        db.close()
