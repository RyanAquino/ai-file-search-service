from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.orm import Session

from database import get_db_session
from models.user import User
from settings import get_settings, Settings
from google.cloud import storage
from pinecone import Pinecone, ServerlessSpec
import redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_db_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credentials_exception

    user = session.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception

    return user


@lru_cache
def get_gcp_storage_client(bucket_name: str):
    storage_client = storage.Client()
    full_bucket_name = f"{storage_client.project}_{bucket_name}"

    if not storage_client.bucket(full_bucket_name).exists():
        storage_client.create_bucket(full_bucket_name)

    return storage_client


def get_gcp_client(settings: Settings = Depends(get_settings)):
    return get_gcp_storage_client(settings.bucket_name)


def get_pinecone_index(settings: Settings = Depends(get_settings)):
    pc = Pinecone(api_key=settings.pinecone_api_key, pool_threads=30)
    if not pc.has_index(settings.pinecone_index_name):
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    return pc.Index(settings.pinecone_index_name)


@lru_cache
def get_llm_embedding_client():
    return OpenAIEmbeddings(
        model="text-embedding-ada-002",
    )


def get_redis_client(settings: Settings = Depends(get_settings)):
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_cache_db, decode_responses=True)
    return client
