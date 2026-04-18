from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.persistence.user.models import UserModel


async def get_user_by_email(session: AsyncSession, email: str) -> UserModel | None:
    result: Result = await session.execute(select(UserModel).where(UserModel.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserModel | None:
    return await session.get(UserModel, user_id)


async def list_users_with_accounts(session: AsyncSession) -> list[UserModel]:
    result: Result = await session.execute(
        select(UserModel).options(selectinload(UserModel.accounts)).order_by(UserModel.id)
    )
    return list(result.scalars().unique().all())


async def save_user(session: AsyncSession, user: UserModel) -> UserModel:
    """Persist the user in the current transaction without committing.

    This helper intentionally *does not* commit so transaction control can be
    delegated to a UnitOfWork. It flushes pending changes and refreshes the
    instance so callers can rely on generated primary keys and defaults.
    """
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user
