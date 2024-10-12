"""Auth module."""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db_session
from models.requests import UserRegisterRequest
from models.response import TokenResponse, UserRegisterResponse
from operations.auth import AuthOperations
from settings import Settings, get_settings

router = APIRouter()


@router.post("/login")
def login(
    request_payload: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """
    Login endpoint.

    :param request_payload: request payload of type OAuth2PasswordRequestForm
    :param session: Database session dependency
    :param settings: Application settings dependency
    :return: TokenResponse
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth = AuthOperations(session, settings, pwd_context)
    token = auth.login(request_payload)

    return TokenResponse(access_token=token)


@router.post("/register")
def register(
    request_payload: UserRegisterRequest,
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> UserRegisterResponse:
    """
    Register endpoint.

    :param request_payload: request payload of type UserRegisterRequest
    :param session: Database session dependency
    :param settings: Application settings dependency
    :return: UserRegisterResponse
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth = AuthOperations(session, settings, pwd_context)
    user = auth.register(request_payload.username, request_payload.password)

    return UserRegisterResponse(id=user.id, username=user.username)
