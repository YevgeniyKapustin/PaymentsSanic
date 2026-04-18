from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.persistence.account.models import AccountModel
    from src.infrastructure.persistence.payment.models import PaymentModel
    from src.infrastructure.persistence.user.models import UserModel


class UserRepository(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        """Return a UserModel by id or None."""

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Return a UserModel by email or None."""

    @abstractmethod
    async def save_user(self, user: UserModel) -> UserModel:
        """Persist and return the given user (should commit and refresh)."""

    @abstractmethod
    async def delete_user(self, user: UserModel) -> None:
        """Delete the provided user and commit the transaction."""

    @abstractmethod
    async def list_users_with_accounts(self) -> list[UserModel]:
        """Return the list of users with their accounts preloaded."""

    @abstractmethod
    async def list_user_accounts(self, user_id: int) -> list[AccountModel]:
        """Return accounts for a given user id."""

    @abstractmethod
    async def list_user_payments(self, user_id: int) -> list[PaymentModel]:
        """Return payments for a given user id."""
