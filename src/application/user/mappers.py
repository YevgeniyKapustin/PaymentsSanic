from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import TYPE_CHECKING

from src.domain.user.dto import AccountDTO, PaymentDTO, UserDTO, UserWithAccountsDTO

if TYPE_CHECKING:
    from src.infrastructure.persistence.account.models import AccountModel
    from src.infrastructure.persistence.payment.models import PaymentModel
    from src.infrastructure.persistence.user.models import UserModel


def _model_to_dict_by_fields(model: object, dto_class: type[object]) -> dict:
    """Return dict of dto_field_name: value taken from model attributes when present.

    Ensures dto_class is a dataclass type to avoid runtime errors from dataclasses.fields.
    """
    if not is_dataclass(dto_class):
        raise TypeError("dto_class must be a dataclass type")

    result: dict = {}
    for f in fields(dto_class):
        if hasattr(model, f.name):
            result[f.name] = getattr(model, f.name)
    return result


def map_user_to_dto(user: UserModel) -> UserDTO:
    """Map an ORM UserModel to the UserDTO value object using dataclass fields."""
    return UserDTO(**_model_to_dict_by_fields(user, UserDTO))


def map_user_with_accounts_to_dto(user: UserModel) -> UserWithAccountsDTO:
    """Map an ORM UserModel with preloaded accounts to UserWithAccountsDTO."""
    user_data = _model_to_dict_by_fields(user, UserWithAccountsDTO)
    user_data.pop("accounts", None)
    accounts = [
        AccountDTO(**_model_to_dict_by_fields(acc, AccountDTO))
        for acc in getattr(user, "accounts", [])
    ]
    return UserWithAccountsDTO(**user_data, accounts=accounts)


def map_account_to_dto(acc: AccountModel) -> AccountDTO:
    """Map an ORM AccountModel to AccountDTO."""
    return AccountDTO(**_model_to_dict_by_fields(acc, AccountDTO))


def map_payment_to_dto(p: PaymentModel) -> PaymentDTO:
    """Map an ORM PaymentModel to PaymentDTO."""
    return PaymentDTO(**_model_to_dict_by_fields(p, PaymentDTO))
