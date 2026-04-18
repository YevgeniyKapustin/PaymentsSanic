from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt

from src.bootstrap.config import get_settings
from src.infrastructure.persistence.user.models import UserModel


def create_access_token(user: UserModel) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.auth.access_token_expire_minutes)
    payload = {"sub": str(user.id), "role": user.role.value, "exp": expire}
    return cast(
        str,
        jwt.encode(payload, settings.auth.jwt_secret_key, algorithm=settings.auth.jwt_algorithm),
    )


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return cast(
        dict[str, Any],
        jwt.decode(token, settings.auth.jwt_secret_key, algorithms=[settings.auth.jwt_algorithm]),
    )
