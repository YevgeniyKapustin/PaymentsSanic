from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.payment.ports import PaymentWebhookRepository
from src.infrastructure.persistence.account.models import AccountModel
from src.infrastructure.persistence.account.repositories import get_account_for_user
from src.infrastructure.persistence.payment.models import PaymentModel
from src.infrastructure.persistence.payment.repositories import get_payment_by_transaction_id
from src.infrastructure.persistence.user.models import UserModel
from src.infrastructure.persistence.user.repositories import get_user_by_id


class SqlAlchemyPaymentWebhookRepository(PaymentWebhookRepository):
    """SQLAlchemy-based implementation of PaymentWebhookRepository.

    This class adapts repository methods to concrete SQLAlchemy calls while
    preserving the abstract interface used by the application use cases.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_payment_by_transaction_id(self, transaction_id: str) -> PaymentModel | None:
        """Return a payment by external transaction id or None if not found."""
        return await get_payment_by_transaction_id(self._session, transaction_id)

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        """Return a UserModel by id or None."""
        return await get_user_by_id(self._session, user_id)

    async def get_account_for_user(
        self, account_id: int, user_id: int, *, lock: bool = False
    ) -> AccountModel | None:
        """Return an account for given user; optionally lock it for update."""
        return await get_account_for_user(self._session, account_id, user_id, lock=lock)

    async def get_account_by_id(self, account_id: int) -> AccountModel | None:
        """Return an account by its id or None."""
        return await self._session.get(AccountModel, account_id)

    def create_account(self, account_id: int, user_id: int, balance: Decimal) -> AccountModel:
        """Instantiate and add an AccountModel to the session."""
        account = AccountModel(id=account_id, user_id=user_id, balance=balance)
        self._session.add(account)
        return account

    def create_payment(
        self, transaction_id: str, user_id: int, account_id: int, amount: Decimal
    ) -> PaymentModel:
        """Instantiate and add a PaymentModel to the session."""
        payment = PaymentModel(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
        )
        self._session.add(payment)
        return payment

    async def flush(self) -> None:
        """Flush pending changes to the database."""
        await self._session.flush()

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self._session.rollback()

    async def refresh(self, instance: AccountModel | PaymentModel) -> None:
        """Refresh state of an ORM instance from the database."""
        await self._session.refresh(instance)
