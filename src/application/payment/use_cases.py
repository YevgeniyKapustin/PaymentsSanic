from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import IntegrityError

from src.application.payment.commands import ProcessPaymentWebhookCommand
from src.application.payment.ports import PaymentWebhookRepository
from src.application.uow import UnitOfWork
from src.domain.payment.dto import ProcessedPaymentWebhookDTO
from src.domain.user.role import Role
from src.infrastructure.persistence.payment.models import PaymentModel
from src.infrastructure.security.signature import build_webhook_signature
from src.shared.exceptions import NotFoundError, ValidationError

if TYPE_CHECKING:
    from src.application.user.ports import UserRepository
    from src.infrastructure.persistence.account.models import AccountModel
    from src.infrastructure.persistence.user.models import UserModel


class RepoUnitOfWork(UnitOfWork):
    """Adapter that exposes a PaymentWebhookRepository as a UnitOfWork.

    This is a small, explicit top-level adapter instead of a nested class.
    """

    def __init__(self, repository: PaymentWebhookRepository) -> None:
        self._repository = repository

    @property
    def payment_repository(self) -> PaymentWebhookRepository:
        return self._repository

    @property
    def user_repository(self) -> UserRepository:
        # This adapter only exposes payment repository operations
        raise NotImplementedError("RepoUnitOfWork does not provide user_repository")

    async def commit(self) -> None:
        await self._repository.commit()

    async def rollback(self) -> None:
        await self._repository.rollback()

    async def flush(self) -> None:
        await self._repository.flush()

    async def refresh(self, instance: AccountModel | PaymentModel) -> None:
        await self._repository.refresh(instance)


class ProcessPaymentWebhookUseCase:
    """Handle an incoming payment webhook using a UnitOfWork abstraction.

    _uow: UnitOfWork

    This reduces direct session management in the use case and centralizes
    transaction control in the UnitOfWork implementation.

    Backwards-compatible: accept either a UnitOfWork instance or a
    PaymentWebhookRepository. If a repository is provided, wrap it into a
    minimal UnitOfWork adapter so tests that pass the repository directly
    keep working.
    """

    def __init__(self, uow: UnitOfWork | PaymentWebhookRepository) -> None:
        self._uow: UnitOfWork

        if isinstance(uow, PaymentWebhookRepository):
            self._uow = RepoUnitOfWork(uow)
        elif isinstance(uow, UnitOfWork):
            self._uow = uow
        else:
            raise TypeError("uow must be UnitOfWork or PaymentWebhookRepository")

    async def execute(self, command: ProcessPaymentWebhookCommand) -> ProcessedPaymentWebhookDTO:
        """Process a payment webhook command.

        Args:
            command: ProcessPaymentWebhookCommand dataclass with webhook data.

        Returns:
            ProcessedPaymentWebhookDTO with payment id, account id, and new balance.

        Raises:
            ValidationError: On invalid signature or account ownership issues.
            NotFoundError: If the referenced user does not exist.
        """
        await self._validate_signature(command)

        repo: PaymentWebhookRepository = self._uow.payment_repository
        existing_payment: PaymentModel | None = await repo.get_payment_by_transaction_id(
            command.transaction_id
        )
        if existing_payment is not None:
            return self._map_to_dto(existing_payment)

        user: UserModel | None = await repo.get_user_by_id(command.user_id)
        if user is None or user.role != Role.USER:
            raise NotFoundError("User not found")

        account: AccountModel = await self._get_or_create_account(command)

        try:
            payload: dict[str, Any] = asdict(command)
            payload.pop("signature", None)
            payment: PaymentModel = repo.create_payment(**payload)
            account.balance += command.amount
            await self._uow.commit()
        except IntegrityError:
            await self._uow.rollback()
            duplicate_payment: PaymentModel | None = await repo.get_payment_by_transaction_id(
                command.transaction_id
            )
            if duplicate_payment is None:
                raise
            return self._map_to_dto(duplicate_payment)

        await self._uow.refresh(payment)
        await self._uow.refresh(account)
        return ProcessedPaymentWebhookDTO(
            payment_id=payment.id,
            account_id=account.id,
            balance=account.balance,
        )

    async def _get_or_create_account(self, command: ProcessPaymentWebhookCommand) -> AccountModel:
        """Return a locked account for update or create a new one.

        The method tries to get a locked account for this user to avoid
        concurrent balance updates. If none exists, it ensures the account
        does not belong to another user and then creates it.
        """
        repo: PaymentWebhookRepository = self._uow.payment_repository
        account: AccountModel | None = await repo.get_account_for_user(
            command.account_id, command.user_id, lock=True
        )
        if account is not None:
            return account

        existing_account: AccountModel | None = await repo.get_account_by_id(command.account_id)
        if existing_account is not None and existing_account.user_id != command.user_id:
            raise ValidationError("Account belongs to another user")

        account = repo.create_account(command.account_id, command.user_id, Decimal("0.00"))
        await self._uow.flush()
        return account

    @staticmethod
    async def _validate_signature(command: ProcessPaymentWebhookCommand) -> None:
        """Validate webhook signature using canonical command fields.

        This method removes the signature field and computes the expected
        signature to compare. It raises ValidationError on mismatch.
        """
        payload = asdict(command)
        payload.pop("signature", None)
        expected_signature = build_webhook_signature(**payload)
        if expected_signature != command.signature:
            raise ValidationError("Invalid signature")

    @staticmethod
    def _map_to_dto(payment: PaymentModel) -> ProcessedPaymentWebhookDTO:
        """Map a PaymentModel instance to the public DTO used by the API."""
        return ProcessedPaymentWebhookDTO(
            payment_id=payment.id,
            account_id=payment.account_id,
            balance=payment.account.balance,
        )
