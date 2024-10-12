from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from database import get_db_session
from models.user import User
from settings import get_settings, Settings
from google.cloud import storage

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


def get_gcp_client(settings: Settings = Depends(get_settings)):
    storage_client = storage.Client()
    bucket_name = f"{storage_client.project}_{settings.bucket_name}"

    if not storage_client.bucket(bucket_name).exists():
        storage_client.create_bucket(bucket_name)

    return storage_client
