from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.persistence.payment.models import PaymentModel


async def list_user_payments(session: AsyncSession, user_id: int) -> list[PaymentModel]:
    result: Result = await session.execute(
        select(PaymentModel).where(PaymentModel.user_id == user_id).order_by(PaymentModel.id)
    )
    return list(result.scalars().all())


async def get_payment_by_transaction_id(
    session: AsyncSession, transaction_id: str
) -> PaymentModel | None:
    result: Result = await session.execute(
        select(PaymentModel)
        .where(PaymentModel.transaction_id == transaction_id)
        .options(selectinload(PaymentModel.account))
    )
    return result.scalar_one_or_none()
