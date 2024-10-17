"""Auth operations module."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.response import UserToken
from models.user import User
from settings import Settings


class AuthOperations:
    """Auth operations class."""

    def __init__(self, session: Session, settings: Settings, pwd_context: CryptContext):
        """
        Inject class dependencies.

        :param session: Database session
        :param settings: Application settings
        :param pwd_context: Auth CryptContext
        """
        self.pwd_context = pwd_context
        self.session = session
        self.settings = settings

    def login(self, request_payload: OAuth2PasswordRequestForm) -> str:
        """
        Login users endpoint.

        :param request_payload: OAuth2PasswordRequestForm - username and password
        :return: JWT token
        """
        user = (
            self.session.query(User)
            .filter(User.username == request_payload.username)
            .first()
        )

        logger.info(f"Logging in user: {request_payload.username}")

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {request_payload.username} not found.",
            )

        if not self.pwd_context.verify(request_payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_token_data = UserToken(
            sub=user.username,
            exp=datetime.now(timezone.utc)
            + timedelta(minutes=self.settings.token_exp_minutes),
            iat=datetime.now(timezone.utc),
        )
        encoded_jwt = jwt.encode(
            user_token_data.model_dump(),
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

        return encoded_jwt

    def register(self, username: str, password: str) -> User:
        """
        Register Users.

        :param username: user name
        :param password: password
        :return: User object with username and ID
        """
        hashed_pw = self.pwd_context.hash(password)
        try:
            user = User(
                username=username,
                hashed_password=hashed_pw,
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError as exc:
            logger.error(f"IntegrityError: {exc}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username {username} already exists.",
            ) from exc

        return user
