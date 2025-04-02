from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.users.users import UserRepository
from app.repositories.users.tokens import TokenRepository
from app.controllers.users.auth_controller import AuthController
from app.db.base import get_db


def get_user_repo(
    session: AsyncSession = Depends(get_db)
) -> UserRepository:
    """
    Get a user repository instance.

    Args:
        session (AsyncSession): The database session.

    Returns:
        UserRepository: The user repository instance.
    """
    return UserRepository(session)

def get_token_repo(
    session: AsyncSession = Depends(get_db)
) -> TokenRepository:
    """
    Get a token repository instance.

    Args:
        session (AsyncSession): The database session.

    Returns:
        TokenRepository: The token repository instance.
    """
    return TokenRepository(session)

def get_auth_controller(
    user_repo: UserRepository = Depends(get_user_repo),
    token_repo: TokenRepository = Depends(get_token_repo),
) -> AuthController:
    """
    Get an authentication controller instance.

    Args:
        user_repo (UserRepository): The user repository instance.
        token_repo (TokenRepository): The token repository instance.

    Returns:
        AuthController: The authentication controller instance.
    """
    return AuthController(user_repo, token_repo)
