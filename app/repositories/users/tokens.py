from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.db.models.users import TokenTable

class TokenRepository:
    """
    Repository for token related operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the TokenRepository with the given session

        Args:
            session (AsyncSession): The database session
        """
        self.session = session

    async def get_by_refresh_token(
        self, refresh_token: str
    ) -> TokenTable | None:
        """
        Get a token by its refresh token

        Args:
            refresh_token (str): The refresh token

        Returns:
            TokenTable | None: The token if found, None otherwise
        """
        result = await self.session.execute(
            select(TokenTable).filter(
                TokenTable.refresh_token == refresh_token,
                TokenTable.status
            )
        )
        return result.scalars().first()

    async def invalidate_all_tokens(
        self, user_id: int
    ) -> None:
        """
        Invalidate all tokens for the given user

        Args:
            user_id (int): The user id
        """
        stmt = update(TokenTable).filter(
            TokenTable.user_id == user_id
        ).values(status=False)
        await self.session.execute(stmt)
        await self.session.commit()

    async def invalidate_token(
        self, refresh_token: str
    ) -> None:
        """
        Invalidate the given token

        Args:
            refresh_token (str): The refresh token
        """
        stmt = update(TokenTable).filter(
            TokenTable.refresh_token == refresh_token
        ).values(status=False)
        await self.session.execute(stmt)
        await self.session.commit()
