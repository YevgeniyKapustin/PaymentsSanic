from abc import ABC, abstractmethod
from decimal import Decimal

from src.infrastructure.persistence.account.models import AccountModel
from src.infrastructure.persistence.payment.models import PaymentModel
from src.infrastructure.persistence.user.models import UserModel


class PaymentWebhookRepository(ABC):
    @abstractmethod
    async def get_payment_by_transaction_id(self, transaction_id: str) -> PaymentModel | None:
        """Return an already processed payment by external transaction id."""

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        """Return a user by identifier."""

    @abstractmethod
    async def get_account_for_user(
        self, account_id: int, user_id: int, *, lock: bool = False
    ) -> AccountModel | None:
        """Return a user's account, optionally locking it for update."""

    @abstractmethod
    async def get_account_by_id(self, account_id: int) -> AccountModel | None:
        """Return an account by identifier."""

    @abstractmethod
    def create_account(self, account_id: int, user_id: int, balance: Decimal) -> AccountModel:
        """Instantiate and add a new account to the current unit of work."""

    @abstractmethod
    def create_payment(
        self, transaction_id: str, user_id: int, account_id: int, amount: Decimal
    ) -> PaymentModel:
        """Instantiate and add a new payment to the current unit of work."""

    @abstractmethod
    async def flush(self) -> None:
        """Flush the current unit of work."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current unit of work."""

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current unit of work."""

    @abstractmethod
    async def refresh(self, instance: AccountModel | PaymentModel) -> None:
        """Refresh an instance from the database."""
