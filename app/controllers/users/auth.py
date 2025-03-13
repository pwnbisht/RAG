from app.repositories.users.users import UserRepository
from app.repositories.users.tokens import TokenRepository
from app.db.models.users import User
from app.schemas.users.users import UserCreate, TokenSchema
from app.utils.security import hash_password, verify_password, create_tokens
from app.core.exceptions import BadRequestException, ForbiddenException
from jose import jwt, JWTError
from app.core.config import get_settings

class AuthController:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.settings = get_settings()

    async def signup(self, user: UserCreate) -> User:
        # Check if username or email already exists
        if await self.user_repo.get_by_username_or_email(user.username, user.email):
            raise BadRequestException("Username or email already exists")

        hashed_password = hash_password(user.password)
        new_user = await self.user_repo.create(user.username, user.email, hashed_password)
        return new_user

    async def login(self, username: str, password: str) -> TokenSchema:
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise BadRequestException("Incorrect username or password")
        return await create_tokens(user.id, self.user_repo.session)

    async def logout(self, user_id: int) -> dict:
        await self.token_repo.invalidate_all_tokens(user_id)
        return {"message": "Logout successful."}

    async def refresh_tokens(self, refresh_token: str) -> TokenSchema:
        try:
            payload = jwt.decode(
                refresh_token,
                self.settings.JWT_REFRESH_SECRET_KEY,
                algorithms=[self.settings.algorithm]
            )
            user_id = payload.get("sub")
            if user_id is None:
                raise ForbiddenException("Invalid refresh token payload.")
            user_id = int(user_id)
        except JWTError:
            raise ForbiddenException("Invalid refresh token.")

        token_record = await self.token_repo.get_by_refresh_token(refresh_token)
        if not token_record:
            raise ForbiddenException("Refresh token has been invalidated or does not exist.")

        # Invalidate the old refresh token
        await self.token_repo.invalidate_token(refresh_token)
        return await create_tokens(user_id, self.user_repo.session)
