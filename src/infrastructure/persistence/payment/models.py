from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base
from src.infrastructure.db.db_types import CreatedAt, MoneyAmount, Str255, UpdatedAt

if TYPE_CHECKING:
    from src.infrastructure.persistence.account.models import AccountModel
    from src.infrastructure.persistence.user.models import UserModel


class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[Str255] = mapped_column(unique=True, nullable=False, index=True)
    amount: Mapped[MoneyAmount] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    user: Mapped[UserModel] = relationship(back_populates="payments")
    account: Mapped[AccountModel] = relationship(back_populates="payments")
