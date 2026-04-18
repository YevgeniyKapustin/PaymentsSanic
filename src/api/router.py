from typing import Any

from sanic import Blueprint

from src.api.admin.router import router as admin_router
from src.api.auth.router import router as auth_router
from src.api.health.router import router as health_router
from src.api.users.router import router as users_router
from src.api.webhooks.router import router as webhooks_router
from src.bootstrap.config import Settings


def create_api_router(settings: Settings) -> Any:
    """Create API router grouping all sub-routers under a common prefix.

    Returns a Blueprint or other grouping object depending on sanic implementation.
    """
    return Blueprint.group(
        health_router,
        auth_router,
        users_router,
        admin_router,
        webhooks_router,
        url_prefix="/api/v1",
    )
