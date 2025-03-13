from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url)
Base = declarative_base()


async def get_db():
    async with AsyncSession(engine) as session:
        yield session


@asynccontextmanager
async def get_db_session():
    db_gen = get_db()
    session = await db_gen.__anext__()
    try:
        yield session
    finally:
        await session.close()