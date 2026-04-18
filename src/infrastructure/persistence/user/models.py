from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.user.role import Role
from src.infrastructure.db.base import Base
from src.infrastructure.db.db_types import CreatedAt, Str255, UpdatedAt

if TYPE_CHECKING:
    from src.infrastructure.persistence.account.models import AccountModel
    from src.infrastructure.persistence.payment.models import PaymentModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[Str255] = mapped_column(unique=True, nullable=False, index=True)
    full_name: Mapped[Str255] = mapped_column(nullable=False)
    password_hash: Mapped[Str255] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role"), nullable=False, default=Role.USER
    )
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    accounts: Mapped[list[AccountModel]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    payments: Mapped[list[PaymentModel]] = relationship(back_populates="user")
