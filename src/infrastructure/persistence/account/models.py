from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base
from src.infrastructure.db.db_types import CreatedAt, MoneyAmount, UpdatedAt

if TYPE_CHECKING:
    from src.infrastructure.persistence.payment.models import PaymentModel
    from src.infrastructure.persistence.user.models import UserModel


class AccountModel(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[MoneyAmount] = mapped_column(nullable=False, default=0)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    user: Mapped[UserModel] = relationship(back_populates="accounts")
    payments: Mapped[list[PaymentModel]] = relationship(back_populates="account")
