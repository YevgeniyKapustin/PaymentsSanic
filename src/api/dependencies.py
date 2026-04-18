from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.persistence.user.repository import SqlAlchemyUserRepository


def get_uow(session: AsyncSession) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_user_repository(session: AsyncSession) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)
