from decimal import Decimal

import bcrypt as _bcrypt
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import src.infrastructure.persistence  # noqa: F401
from src.infrastructure.db.base import Base
from src.infrastructure.persistence.account.models import AccountModel
from src.infrastructure.persistence.payment.repository import SqlAlchemyPaymentWebhookRepository
from src.infrastructure.persistence.user.models import Role, UserModel
from src.infrastructure.security.password import hash_password

# passlib 1.7.4 is incompatible with bcrypt 5.x: detect_wrap_bug passes a 200+ byte password
# which bcrypt 5.x rejects with ValueError. Patch bcrypt.hashpw to truncate long passwords
# so passlib's internal bug-detection routine can complete.
_original_hashpw = _bcrypt.hashpw


def _hashpw_truncate(password: bytes, salt: bytes) -> bytes:
    return _original_hashpw(password[:72] if len(password) > 72 else password, salt)


_bcrypt.hashpw = _hashpw_truncate


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as db_session:
        yield db_session

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(session: AsyncSession) -> UserModel:
    user = UserModel(
        email="user@example.com",
        full_name="Test User",
        password_hash=hash_password("userpass123"),
        role=Role.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(session: AsyncSession) -> UserModel:
    admin = UserModel(
        email="admin@example.com",
        full_name="Test Admin",
        password_hash=hash_password("adminpass123"),
        role=Role.ADMIN,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def test_account(session: AsyncSession, test_user: UserModel) -> AccountModel:
    account = AccountModel(user_id=test_user.id, balance=Decimal("100.00"))
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


@pytest_asyncio.fixture
def webhook_repo(session: AsyncSession) -> SqlAlchemyPaymentWebhookRepository:
    return SqlAlchemyPaymentWebhookRepository(session)
