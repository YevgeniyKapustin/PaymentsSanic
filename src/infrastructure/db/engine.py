import logging
from collections.abc import AsyncIterator
from functools import lru_cache

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

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def init(self) -> None:
        """Initialize the async engine and sessionmaker if not already done."""
        if self._engine is not None and self._sessionmaker is not None:
            return

        settings = get_settings()
        logger.info("Initializing database engine")
        self._engine = create_async_engine(
            settings.database.database_url, future=True, pool_pre_ping=True
        )
        self._sessionmaker = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def dispose(self) -> None:
        """Dispose the engine and clear internal references."""
        if self._engine is not None:
            logger.info("Disposing database engine")
            await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

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


@lru_cache
def get_database_manager() -> DatabaseManager:
    """Return a singleton DatabaseManager instance."""
    return DatabaseManager()


def db_session() -> AsyncSession:
    """Shortcut for getting a new session context manager from the global manager."""
    return get_database_manager().session()
