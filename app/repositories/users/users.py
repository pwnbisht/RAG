from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.db.models.users import User


class UserRepository:
    """
    Repository for user-related operations.

    Attributes:
        session (AsyncSession): The database session used for operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository with the given session.

        Args:
            session (AsyncSession): The database session.
        """
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        """
        Get a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User | None: The user if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).filter(User.username == username)
        )
        return result.scalars().first()

    async def get_by_username_or_email(self, username: str, email: str) -> User | None:
        """
        Get a user by their username or email.

        Args:
            username (str): The username of the user.
            email (str): The email of the user.

        Returns:
            User | None: The user if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).filter(
                or_(User.username == username, User.email == email)
            )
        )
        return result.scalars().first()

    async def create(self, username: str, email: str, hashed_password: str) -> User:
        """
        Create a new user with the given details.

        Args:
            username (str): The username for the new user.
            email (str): The email for the new user.
            hashed_password (str): The hashed password for the new user.

        Returns:
            User: The newly created user.
        """
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
