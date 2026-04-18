import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.auth.use_cases import AuthenticateUserUseCase
from src.infrastructure.persistence.user.models import UserModel
from src.infrastructure.persistence.user.repository import SqlAlchemyUserRepository
from src.shared.exceptions import AuthError


@pytest.mark.asyncio
async def test_login_success_user(session: AsyncSession, test_user: UserModel) -> None:
    use_case = AuthenticateUserUseCase(SqlAlchemyUserRepository(session))
    result = await use_case.execute("user@example.com", "userpass123")
    assert result.access_token


@pytest.mark.asyncio
async def test_login_success_admin(session: AsyncSession, test_admin: UserModel) -> None:
    use_case = AuthenticateUserUseCase(SqlAlchemyUserRepository(session))
    result = await use_case.execute("admin@example.com", "adminpass123")
    assert result.access_token


@pytest.mark.asyncio
async def test_login_wrong_password(session: AsyncSession, test_user: UserModel) -> None:
    use_case = AuthenticateUserUseCase(SqlAlchemyUserRepository(session))
    with pytest.raises(AuthError):
        await use_case.execute("user@example.com", "wrongpassword")


@pytest.mark.asyncio
async def test_login_user_not_found(session: AsyncSession) -> None:
    use_case = AuthenticateUserUseCase(SqlAlchemyUserRepository(session))
    with pytest.raises(AuthError):
        await use_case.execute("nonexistent@example.com", "anypassword")
