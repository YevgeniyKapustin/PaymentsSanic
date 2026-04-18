from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.user.ports import UserRepository
from src.infrastructure.persistence.account import repositories as account_repos
from src.infrastructure.persistence.account.models import AccountModel
from src.infrastructure.persistence.payment import repositories as payment_repos
from src.infrastructure.persistence.payment.models import PaymentModel
from src.infrastructure.persistence.user import repositories as user_repos
from src.infrastructure.persistence.user.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        return await user_repos.get_user_by_id(self._session, user_id)

    async def get_user_by_email(self, email: str) -> UserModel | None:
        return await user_repos.get_user_by_email(self._session, email)

    async def save_user(self, user: UserModel) -> UserModel:
        # re-use existing helper that flushes and refreshes but does not commit
        return await user_repos.save_user(self._session, user)

    async def delete_user(self, user: UserModel) -> None:
        await self._session.delete(user)
        await self._session.flush()

    async def list_users_with_accounts(self) -> list[UserModel]:
        return await user_repos.list_users_with_accounts(self._session)

    async def list_user_accounts(self, user_id: int) -> list[AccountModel]:
        return await account_repos.list_user_accounts(self._session, user_id)

    async def list_user_payments(self, user_id: int) -> list[PaymentModel]:
        return await payment_repos.list_user_payments(self._session, user_id)
