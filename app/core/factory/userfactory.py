from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.users.users import UserRepository
from app.repositories.users.tokens import TokenRepository
from app.controllers.users.auth import AuthController
from app.db.base import get_db


def get_user_repo(
    session: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(session)

def get_token_repo(
    session: AsyncSession = Depends(get_db)
) -> TokenRepository:
    return TokenRepository(session)

def get_auth_controller(
    user_repo: UserRepository = Depends(get_user_repo),
    token_repo: TokenRepository = Depends(get_token_repo),
) -> AuthController:
    return AuthController(user_repo, token_repo)
