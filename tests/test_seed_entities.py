from decimal import Decimal

import pytest

from src.infrastructure.persistence.account.models import AccountModel
from src.infrastructure.persistence.user.models import Role, UserModel
from src.infrastructure.security.password import hash_password, verify_password


@pytest.mark.asyncio
async def test_can_create_test_user_account_and_admin(session):
    user = UserModel(
        email="user@example.com",
        full_name="Test User",
        password_hash=hash_password("userpass123"),
        role=Role.USER,
    )
    admin = UserModel(
        email="admin@example.com",
        full_name="Test Admin",
        password_hash=hash_password("adminpass123"),
        role=Role.ADMIN,
    )

    session.add_all([user, admin])
    await session.flush()

    account = AccountModel(user_id=user.id, balance=Decimal("100.00"))
    session.add(account)
    await session.commit()

    assert user.id is not None
    assert admin.id is not None
    assert account.id is not None
    assert account.user_id == user.id
    assert account.balance == Decimal("100.00")
    assert verify_password("userpass123", user.password_hash)
    assert verify_password("adminpass123", admin.password_hash)
