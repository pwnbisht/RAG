from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.users import TokenTable
from app.schemas.users.users import TokenSchema


settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY


def hash_password(password: str) -> str:
    """
    Hashes the given password and returns the hashed password
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str) -> bool:
    """
    Verifies if the given plain password matches the hashed password.

    :param plain_password: The plain text password to verify.
    :param hashed_password: The hashed password to compare against.
    :return: True if the passwords match, False otherwise.
    """

    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Creates a JWT access token for the given subject.

    :param subject: The subject of the token, usually a user ID.
    :param expires_delta: The time delta for when the token should expire.
        If None, the token expires after ACCESS_TOKEN_EXPIRE_MINUTES minutes.
    :return: The generated JWT access token.
    """
    expires = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    to_encode = {"exp": expires, "sub": str(subject)}
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        settings.algorithm
    )


def create_refresh_token(
    subject: str | Any,
    expires_delta: int | None = None,
) -> str:
    """
    Creates a JWT refresh token for the given subject.

    :param subject: The subject of the token, usually a user ID.
    :param expires_delta: The time delta for when the token should expire.
        If None, the token expires after REFRESH_TOKEN_EXPIRE_MINUTES minutes.
    :return: The generated JWT refresh token.
    """

    now = datetime.now(timezone.utc)
    expires = now + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    ) if expires_delta is None else now + expires_delta
    
    to_encode = {"exp": expires, "sub": str(subject)}
    return jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET_KEY,
        settings.algorithm
    )


async def create_tokens(
    id: int,
    db: AsyncSession
) -> dict:
    """
    Creates access and refresh tokens for the given user ID and
    stores them in the database.

    :param id: The user ID to create tokens for.
    :param db: The database session to use.
    :return: A dictionary containing the access and refresh tokens.
    """
    access = create_access_token(id)
    refresh = create_refresh_token(id)
    
    token_db = TokenTable(
        user_id=id,  access_token=access, 
        refresh_token=refresh, status=True
    )
    await db.merge(token_db)
    await db.commit()
    
    return TokenSchema(access_token=access, refresh_token=refresh)
