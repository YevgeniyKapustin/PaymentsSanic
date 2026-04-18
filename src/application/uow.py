from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.application.payment.ports import PaymentWebhookRepository
from src.application.user.ports import UserRepository


class UnitOfWork(ABC):
    @property
    @abstractmethod
    def payment_repository(self) -> PaymentWebhookRepository:
        """Return repository instance used for payment-related operations."""

    @property
    @abstractmethod
    def user_repository(self) -> UserRepository:
        """Return repository instance used for user-related operations."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit the unit of work transaction."""

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the unit of work transaction."""

    @abstractmethod
    async def flush(self) -> None:
        """Flush pending changes to the database."""

    @abstractmethod
    async def refresh(self, instance: Any) -> None:
        """Refresh an instance from the database."""
