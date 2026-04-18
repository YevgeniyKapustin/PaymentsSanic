from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from http import HTTPStatus
from typing import Concatenate, ParamSpec, TypeVar, cast

import jwt
from sanic import Request

from src.api.common import error_response
from src.api.dependencies import get_user_repository
from src.domain.user.role import Role
from src.infrastructure.db.engine import db_session
from src.infrastructure.persistence.user.models import UserModel
from src.infrastructure.security.token_codec import decode_access_token
from src.shared.exceptions import AuthError


async def get_current_user(request: Request) -> UserModel:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise AuthError("Missing bearer token")
    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        raise AuthError("Missing bearer token")

    try:
        payload: dict[str, object] = decode_access_token(token)
        payload_sub = payload["sub"]
        if not isinstance(payload_sub, str):
            raise AuthError("Invalid token")

        user_id = int(payload_sub)

    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise AuthError("Invalid token") from exc

    async with db_session() as session:
        repo = get_user_repository(session)
        user: UserModel | None = await repo.get_user_by_id(user_id)
        if user is None:
            raise AuthError("User not found")
        return user


P = ParamSpec("P")
R = TypeVar("R")


def require_role(
    role: Role,
) -> Callable[
    [Callable[Concatenate[Request, P], Awaitable[R]]],
    Callable[Concatenate[Request, P], Awaitable[R]],
]:
    def decorator(
        handler: Callable[Concatenate[Request, P], Awaitable[R]],
    ) -> Callable[Concatenate[Request, P], Awaitable[R]]:
        @wraps(handler)
        async def wrapped(request: Request, *args: P.args, **kwargs: P.kwargs) -> R:
            user = await get_current_user(request)
            if user.role != role:
                return cast(
                    R,
                    error_response(
                        status=HTTPStatus.FORBIDDEN,
                        code="forbidden",
                        message="Forbidden",
                        request=request,
                    ),
                )
            request.ctx.user = user
            return await handler(request, *args, **kwargs)

        return wrapped

    return decorator
