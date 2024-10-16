"""Configuration tests module."""

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from dependencies import (
    get_current_user,
    get_db_session,
    get_gcp_client,
    get_llm_embedding_client,
    get_pinecone_index,
    get_redis_client,
)
from main import create_app
from settings import get_settings

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_gcp_client():
    """Overridden gcp_client app dependency."""

    class MockGCPClient:
        project = "test-project"

        def blob(self, name):
            return self

        @staticmethod
        def upload_from_file(*args, **kwargs):
            return None

        def bucket(self, name):
            return self

        @staticmethod
        def generate_signed_url(**kwargs):
            return "signed-url"

    return MockGCPClient()


def override_get_pinecone_index():
    """Overridden get_pinecone_index app dependency."""

    class MockPineconeIndex:

        @staticmethod
        def upsert(*args, **kwargs):
            return None

        @staticmethod
        def query(*args, **kwargs):
            return {}

    return MockPineconeIndex()


def override_get_llm_embedding_client():
    """Overridden get_llm_embedding_client app dependency."""

    class MockOpenAIEmbeddings:

        @staticmethod
        async def aembed_documents(texts):
            return [np.random.rand(1536)]

        @staticmethod
        def embed_query(text):
            return np.random.rand(1536)

    return MockOpenAIEmbeddings()


def override_get_redis_client():
    """Overridden get_redis_client app dependency."""

    class MockRedisClient:

        @staticmethod
        def get(key):
            return None

        @staticmethod
        def set(*args, **kwargs):
            return None

    return MockRedisClient()


def override_get_settings():
    """Overridden get_settings app dependency."""

    class MockSettings:
        bucket_name = "test-bucket"
        token_exp_minutes = 15
        jwt_secret_key = "test-secret"
        jwt_algorithm = "HS256"
        max_file_upload_count = 5
        max_file_bytes_size = 25000000
        openai_api_key = ""
        db_url = ""
        gcp_storage_exp_minutes = 15
        pinecone_api_key = ""
        embedding_chunk_size = 200
        embedding_namespace = "sample-embedding-name-space"
        redis_cache_exp = 15

    return MockSettings()


@pytest.fixture
def db_session():
    """Database session fixture."""

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """
    Not logged in client fixture
    :param db_session: fixture dependency of mock database session
    """

    def override_get_db():
        yield db_session

    app = create_app(disable_limiter=True)
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def login_client(db_session):
    """
    Login client fixture.
    :param db_session: fixture dependency of mock database session
    """

    def override_get_db():
        yield db_session

    app = create_app(disable_limiter=True)
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: None
    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_gcp_client] = override_gcp_client
    app.dependency_overrides[get_pinecone_index] = override_get_pinecone_index
    app.dependency_overrides[get_redis_client] = override_get_redis_client
    app.dependency_overrides[get_llm_embedding_client] = (
        override_get_llm_embedding_client
    )

    with TestClient(app) as test_client:
        yield test_client, app
