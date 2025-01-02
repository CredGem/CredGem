from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.core.settings import settings
from src.utils.singleton import SingletonMeta

Base = declarative_base()


class DBManager(metaclass=SingletonMeta):
    def __init__(self):
        self._engine = None
        self._async_session_maker = None

    @property
    def AsyncSessionMaker(self) -> async_sessionmaker[AsyncSession]:
        if not self._async_session_maker:
            raise ValueError("Database connection not initialized")
        return self._async_session_maker

    async def init_db_connection(self):
        """Initialize all database connections"""
        self._engine = create_async_engine(
            settings.ASYNC_DATABASE_URL, echo=True, future=True
        )

        self._async_session_maker = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        await self.ping_db()

    async def disconnect(self):
        assert self._engine is not None
        await self._engine.dispose()

    async def ping_db(self) -> bool:
        """Check if database connection is alive"""
        async with self.AsyncSessionMaker() as session:
            await session.execute(text("SELECT 1"))
            await session.commit()
        return True
