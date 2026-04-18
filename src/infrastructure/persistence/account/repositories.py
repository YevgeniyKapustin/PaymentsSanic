from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.account.models import AccountModel


async def list_user_accounts(session: AsyncSession, user_id: int) -> list[AccountModel]:
    result: Result = await session.execute(
        select(AccountModel).where(AccountModel.user_id == user_id).order_by(AccountModel.id)
    )
    return list(result.scalars().all())


async def get_account_for_user(
    session: AsyncSession, account_id: int, user_id: int, lock: bool = False
) -> AccountModel | None:
    query = select(AccountModel).where(
        AccountModel.id == account_id, AccountModel.user_id == user_id
    )
    if lock:
        query = query.with_for_update()
    result: Result = await session.execute(query)
    return result.scalar_one_or_none()
