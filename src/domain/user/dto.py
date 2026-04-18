from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.domain.user.role import Role


@dataclass(slots=True)
class UserDTO:
    """Data transfer object representing a user returned by application layer.

    Attributes mirror persistence model fields but are intentionally simple
    value objects used to decouple domain/application layers from ORM models.
    """

    id: int
    email: str
    full_name: str
    role: Role
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class AccountDTO:
    """DTO representing a user's account with its balance and metadata."""

    id: int
    balance: Decimal
    user_id: int
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class PaymentDTO:
    """DTO representing a processed payment record."""

    id: int
    transaction_id: str
    amount: Decimal
    user_id: int
    account_id: int
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class UserWithAccountsDTO(UserDTO):
    """Extended DTO including a list of the user's accounts."""

    accounts: list[AccountDTO]
