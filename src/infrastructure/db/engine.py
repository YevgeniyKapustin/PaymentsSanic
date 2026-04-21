import logging
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.bootstrap.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage lifecycle of the SQLAlchemy AsyncEngine and provide sessions.

    This manager encapsulates engine creation, disposal and provides factory
    methods for obtaining AsyncSession instances. Keeping this logic in a
    single class centralizes database configuration and supports easy
    replacement for testing.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        settings = get_settings()
        logger.info("Initializing database engine")
        self._engine: AsyncEngine = create_async_engine(
            settings.database.database_url, future=True, pool_pre_ping=True
        )
        self._sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def dispose(self) -> None:
        """Dispose the engine and clear internal references."""
        if self._engine is not None:
            logger.info("Disposing database engine")
            await self._engine.dispose()

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        """Return the initialized sessionmaker or raise if not initialized."""
        if self._sessionmaker is None:
            msg = "Database sessionmaker is not initialized."
            raise RuntimeError(msg)
        return self._sessionmaker

    def session(self) -> AsyncSession:
        """Shortcut for getting a new session context manager."""
        return self.get_sessionmaker()()

    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Async context manager yielding a database session."""
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            yield session


def get_database_manager() -> DatabaseManager:
    """Return a singleton DatabaseManager instance."""
    return DatabaseManager()


def db_session() -> AsyncSession:
    """Shortcut for getting a new session context manager from the global manager."""
    return get_database_manager().session()
