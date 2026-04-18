from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

if TYPE_CHECKING:
    from src.infrastructure.persistence.account.models import AccountModel
    from src.infrastructure.persistence.payment.models import PaymentModel
    from src.infrastructure.persistence.user.models import UserModel

from src.api.users.schemas import UserCreateRequest, UserUpdateRequest
from src.application.uow import UnitOfWork
from src.application.user.mappers import (
    map_account_to_dto,
    map_payment_to_dto,
    map_user_to_dto,
    map_user_with_accounts_to_dto,
)
from src.application.user.ports import UserRepository
from src.domain.user.dto import AccountDTO, PaymentDTO, UserDTO, UserWithAccountsDTO
from src.domain.user.role import Role
from src.infrastructure.persistence.user.models import UserModel
from src.infrastructure.security.password import hash_password
from src.shared.exceptions import ConflictError, NotFoundError, ValidationError


class CreateUserUseCase:
    """Create a new regular user in the system using an injected UnitOfWork."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, payload: UserCreateRequest) -> UserDTO:
        repo: UserRepository = self._uow.user_repository
        user = UserModel(
            **payload.model_dump(exclude={"password"}),
            password_hash=hash_password(payload.password),
            role=Role.USER,
        )
        try:
            user = await repo.save_user(user)
            await self._uow.commit()
            return map_user_to_dto(user)
        except IntegrityError as exc:
            await self._uow.rollback()
            raise ConflictError("User with this email already exists") from exc


class UpdateUserUseCase:
    """Update user profile fields for a regular user."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int, payload: UserUpdateRequest) -> UserDTO:
        repo: UserRepository = self._uow.user_repository
        user: UserModel | None = await repo.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        if user.role != Role.USER:
            raise ValidationError("Only regular users can be updated with this endpoint")
        if payload.email is not None:
            user.email = payload.email
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.password is not None:
            user.password_hash = hash_password(payload.password)
        try:
            user = await repo.save_user(user)
            await self._uow.commit()
            return map_user_to_dto(user)
        except IntegrityError as exc:
            await self._uow.rollback()
            raise ConflictError("User with this email already exists") from exc


class DeleteUserUseCase:
    """Delete a regular user. Admin deletion via this endpoint is forbidden."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> None:
        repo: UserRepository = self._uow.user_repository
        user = await repo.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        if user.role != Role.USER:
            raise ValidationError("Admin deletion via this endpoint is not allowed")
        await repo.delete_user(user)
        await self._uow.commit()


class GetUserAccountsUseCase:
    """Return a list of AccountDTO for the given user id using the repository."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> list[AccountDTO]:
        repo: UserRepository = self._uow.user_repository
        accounts: list[AccountModel] = await repo.list_user_accounts(user_id)

        return [map_account_to_dto(acc) for acc in accounts]


class GetUserPaymentsUseCase:
    """Return a list of PaymentDTO for the given user id using the repository."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> list[PaymentDTO]:
        repo: UserRepository = self._uow.user_repository
        payments: list[PaymentModel] = await repo.list_user_payments(user_id)

        return [map_payment_to_dto(p) for p in payments]


class ListUsersWithAccountsUseCase:
    """Return regular users with preloaded accounts for admin listing."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[UserWithAccountsDTO]:
        repo: UserRepository = self._uow.user_repository
        users: list[UserModel] = await repo.list_users_with_accounts()
        return [map_user_with_accounts_to_dto(user) for user in users if user.role == Role.USER]
