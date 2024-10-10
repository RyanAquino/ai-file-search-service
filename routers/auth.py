from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db_session
from operations.auth import AuthOperations
from settings import get_settings, Settings

router = APIRouter()

from fastapi.security import OAuth2PasswordRequestForm


@router.post("/login")
def login(
    request_payload: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth = AuthOperations(session, settings, pwd_context)

    return auth.login(request_payload)


@router.post("/register")
def register(
    username: str,
    password: str,
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth = AuthOperations(session, settings, pwd_context)

    return auth.register(username, password)
