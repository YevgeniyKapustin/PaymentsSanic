from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.user.ports import UserRepository
from src.domain.auth.dto import AuthenticatedUserDTO
from src.infrastructure.security.password import verify_password
from src.infrastructure.security.token_codec import create_access_token
from src.shared.exceptions import AuthError

if TYPE_CHECKING:
    from src.infrastructure.persistence.user.models import UserModel


class AuthenticateUserUseCase:
    """Authenticate a user and return an access token."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def execute(self, email: str, password: str) -> AuthenticatedUserDTO:
        user: UserModel | None = await self._repo.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Invalid credentials")
        return AuthenticatedUserDTO(access_token=create_access_token(user))
