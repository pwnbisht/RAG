from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.db.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).filter(User.username == username)
        )
        return result.scalars().first()

    async def get_by_username_or_email(self, username: str, email: str) -> User | None:
        
        result = await self.session.execute(
            select(User).filter(
                or_(User.username == username, User.email == email)
            )
        )
        return result.scalars().first()

    async def create(self, username: str, email: str, hashed_password: str) -> User:
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user