from decimal import Decimal

import pytest

from src.application.payment.commands import ProcessPaymentWebhookCommand
from src.application.payment.use_cases import ProcessPaymentWebhookUseCase
from src.infrastructure.persistence.account.models import AccountModel
from src.infrastructure.persistence.payment.repository import SqlAlchemyPaymentWebhookRepository
from src.infrastructure.persistence.user.models import UserModel
from src.infrastructure.security.signature import build_webhook_signature
from src.shared.exceptions import NotFoundError, ValidationError


def make_command(
    user_id: int,
    account_id: int,
    amount: Decimal = Decimal("100"),
    transaction_id: str = "tx-test-001",
) -> ProcessPaymentWebhookCommand:
    signature = build_webhook_signature(account_id, amount, transaction_id, user_id)
    return ProcessPaymentWebhookCommand(
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        signature=signature,
    )


@pytest.mark.asyncio
async def test_process_payment_success(
    webhook_repo: SqlAlchemyPaymentWebhookRepository,
    test_user: UserModel,
    test_account: AccountModel,
) -> None:
    use_case = ProcessPaymentWebhookUseCase(webhook_repo)
    command = make_command(test_user.id, test_account.id, Decimal("50"))
    result = await use_case.execute(command)

    assert result.payment_id is not None
    assert result.account_id == test_account.id
    assert result.balance == Decimal("150.00")


@pytest.mark.asyncio
async def test_process_payment_creates_account_if_not_exists(
    webhook_repo: SqlAlchemyPaymentWebhookRepository,
    test_user: UserModel,
) -> None:
    new_account_id = 999
    use_case = ProcessPaymentWebhookUseCase(webhook_repo)
    command = make_command(test_user.id, new_account_id, Decimal("200"))
    result = await use_case.execute(command)

    assert result.account_id == new_account_id
    assert result.balance == Decimal("200")


@pytest.mark.asyncio
async def test_process_payment_invalid_signature(
    webhook_repo: SqlAlchemyPaymentWebhookRepository,
    test_user: UserModel,
    test_account: AccountModel,
) -> None:
    use_case = ProcessPaymentWebhookUseCase(webhook_repo)
    command = ProcessPaymentWebhookCommand(
        transaction_id="tx-bad-sig",
        user_id=test_user.id,
        account_id=test_account.id,
        amount=Decimal("100"),
        signature="invalidsignature",
    )
    with pytest.raises(ValidationError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_process_payment_duplicate_transaction_returns_same_result(
    webhook_repo: SqlAlchemyPaymentWebhookRepository,
    test_user: UserModel,
    test_account: AccountModel,
) -> None:
    use_case = ProcessPaymentWebhookUseCase(webhook_repo)
    command = make_command(test_user.id, test_account.id, Decimal("50"), "tx-duplicate")

    result1 = await use_case.execute(command)
    result2 = await use_case.execute(command)

    assert result1.payment_id == result2.payment_id
    assert result2.balance == Decimal("150.00")


@pytest.mark.asyncio
async def test_process_payment_user_not_found(
    webhook_repo: SqlAlchemyPaymentWebhookRepository,
) -> None:
    use_case = ProcessPaymentWebhookUseCase(webhook_repo)
    command = make_command(user_id=99999, account_id=1)
    with pytest.raises(NotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_process_payment_account_belongs_to_another_user(
    webhook_repo: SqlAlchemyPaymentWebhookRepository,
    test_user: UserModel,
    test_account: AccountModel,
) -> None:
    from src.infrastructure.persistence.user.models import Role
    from src.infrastructure.security.password import hash_password

    other_user = UserModel(
        email="other@example.com",
        full_name="Other User",
        password_hash=hash_password("pass"),
        role=Role.USER,
    )
    webhook_repo._session.add(other_user)
    await webhook_repo._session.commit()
    await webhook_repo._session.refresh(other_user)

    use_case = ProcessPaymentWebhookUseCase(webhook_repo)
    command = make_command(other_user.id, test_account.id, Decimal("50"))
    with pytest.raises(ValidationError):
        await use_case.execute(command)
