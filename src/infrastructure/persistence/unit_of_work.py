from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.payment.ports import PaymentWebhookRepository
from src.application.uow import UnitOfWork
from src.application.user.ports import UserRepository
from src.infrastructure.persistence.payment.repository import SqlAlchemyPaymentWebhookRepository
from src.infrastructure.persistence.user.repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._payment_repo = SqlAlchemyPaymentWebhookRepository(session)
        self._user_repo = SqlAlchemyUserRepository(session)

    @property
    def payment_repository(self) -> PaymentWebhookRepository:
        return self._payment_repo

    @property
    def user_repository(self) -> UserRepository:
        return self._user_repo

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def flush(self) -> None:
        await self._session.flush()

    async def refresh(self, instance: object) -> None:
        await self._session.refresh(instance)
