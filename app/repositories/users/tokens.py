from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.db.models.users import TokenTable

class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_refresh_token(self, refresh_token: str) -> TokenTable | None:
        result = await self.session.execute(
            select(TokenTable).filter(
                TokenTable.refresh_token == refresh_token,
                TokenTable.status
            )
        )
        return result.scalars().first()

    async def invalidate_all_tokens(self, user_id: int) -> None:
        stmt = update(TokenTable).filter(TokenTable.user_id == user_id).values(status=False)
        await self.session.execute(stmt)
        await self.session.commit()

    async def invalidate_token(self, refresh_token: str) -> None:
        stmt = update(TokenTable).filter(TokenTable.refresh_token == refresh_token).values(status=False)
        await self.session.execute(stmt)
        await self.session.commit()