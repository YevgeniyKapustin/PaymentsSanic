from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.users.schemas import UserCreateRequest, UserUpdateRequest
from src.application.user.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserAccountsUseCase,
    GetUserPaymentsUseCase,
    ListUsersWithAccountsUseCase,
    UpdateUserUseCase,
)
from src.infrastructure.persistence.account.models import AccountModel
from src.infrastructure.persistence.payment.models import PaymentModel
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.persistence.user.models import UserModel
from src.shared.exceptions import ConflictError, NotFoundError, ValidationError


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession) -> None:
    use_case = CreateUserUseCase(SqlAlchemyUnitOfWork(session))
    result = await use_case.execute(
        UserCreateRequest(email="new@example.com", full_name="New User", password="pass123")
    )
    assert result.id is not None
    assert result.email == "new@example.com"
    assert result.full_name == "New User"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(session: AsyncSession, test_user: UserModel) -> None:
    use_case = CreateUserUseCase(SqlAlchemyUnitOfWork(session))
    with pytest.raises(ConflictError):
        await use_case.execute(
            UserCreateRequest(email="user@example.com", full_name="Dupe", password="pass123")
        )


@pytest.mark.asyncio
async def test_update_user_email(session: AsyncSession, test_user: UserModel) -> None:
    use_case = UpdateUserUseCase(SqlAlchemyUnitOfWork(session))
    result = await use_case.execute(test_user.id, UserUpdateRequest(email="updated@example.com"))
    assert result.email == "updated@example.com"
    assert result.full_name == test_user.full_name


@pytest.mark.asyncio
async def test_update_user_not_found(session: AsyncSession) -> None:
    use_case = UpdateUserUseCase(SqlAlchemyUnitOfWork(session))
    with pytest.raises(NotFoundError):
        await use_case.execute(99999, UserUpdateRequest(full_name="Ghost"))


@pytest.mark.asyncio
async def test_update_admin_raises_validation_error(
    session: AsyncSession, test_admin: UserModel
) -> None:
    use_case = UpdateUserUseCase(SqlAlchemyUnitOfWork(session))
    with pytest.raises(ValidationError):
        await use_case.execute(test_admin.id, UserUpdateRequest(full_name="New Name"))


@pytest.mark.asyncio
async def test_delete_user(session: AsyncSession, test_user: UserModel) -> None:
    use_case = DeleteUserUseCase(SqlAlchemyUnitOfWork(session))
    await use_case.execute(test_user.id)
    assert await session.get(UserModel, test_user.id) is None


@pytest.mark.asyncio
async def test_delete_user_not_found(session: AsyncSession) -> None:
    use_case = DeleteUserUseCase(SqlAlchemyUnitOfWork(session))
    with pytest.raises(NotFoundError):
        await use_case.execute(99999)


@pytest.mark.asyncio
async def test_delete_admin_raises_validation_error(
    session: AsyncSession, test_admin: UserModel
) -> None:
    use_case = DeleteUserUseCase(SqlAlchemyUnitOfWork(session))
    with pytest.raises(ValidationError):
        await use_case.execute(test_admin.id)


@pytest.mark.asyncio
async def test_get_user_accounts(
    session: AsyncSession, test_user: UserModel, test_account: AccountModel
) -> None:
    use_case = GetUserAccountsUseCase(SqlAlchemyUnitOfWork(session))
    accounts = await use_case.execute(test_user.id)
    assert len(accounts) == 1
    assert accounts[0].id == test_account.id
    assert accounts[0].balance == Decimal("100.00")


@pytest.mark.asyncio
async def test_get_user_accounts_empty(session: AsyncSession, test_user: UserModel) -> None:
    use_case = GetUserAccountsUseCase(SqlAlchemyUnitOfWork(session))
    accounts = await use_case.execute(test_user.id)
    assert accounts == []


@pytest.mark.asyncio
async def test_get_user_payments(
    session: AsyncSession, test_user: UserModel, test_account: AccountModel
) -> None:
    payment = PaymentModel(
        transaction_id="tx-001",
        user_id=test_user.id,
        account_id=test_account.id,
        amount=Decimal("50.00"),
    )
    session.add(payment)
    await session.commit()

    use_case = GetUserPaymentsUseCase(SqlAlchemyUnitOfWork(session))
    payments = await use_case.execute(test_user.id)
    assert len(payments) == 1
    assert payments[0].transaction_id == "tx-001"
    assert payments[0].amount == Decimal("50.00")


@pytest.mark.asyncio
async def test_get_user_payments_empty(session: AsyncSession, test_user: UserModel) -> None:
    use_case = GetUserPaymentsUseCase(SqlAlchemyUnitOfWork(session))
    payments = await use_case.execute(test_user.id)
    assert payments == []


@pytest.mark.asyncio
async def test_list_users_with_accounts_excludes_admin(
    session: AsyncSession, test_user: UserModel, test_admin: UserModel
) -> None:
    account = AccountModel(user_id=test_user.id, balance=Decimal("10.00"))
    session.add(account)
    await session.commit()
    use_case = ListUsersWithAccountsUseCase(SqlAlchemyUnitOfWork(session))
    users = await use_case.execute()
    assert len(users) == 1
    assert users[0].id == test_user.id
    assert users[0].accounts[0].balance == Decimal("10.00")
