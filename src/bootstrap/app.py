from http import HTTPStatus

from sanic import HTTPResponse, Request, Sanic
from sanic_ext import Extend

import src.infrastructure.persistence  # noqa: F401
from src.api.common import error_response
from src.api.router import create_api_router
from src.bootstrap.app_logging import configure_logging
from src.bootstrap.config import Settings, get_settings
from src.infrastructure.db.engine import get_database_manager
from src.shared.exceptions import AuthError, ConflictError, NotFoundError, ValidationError


class SanicApplicationBuilder:
    """Builder for configuring and creating the Sanic application instance.

    Responsibilities:
    - Configure logging and OpenAPI UI settings.
    - Register API blueprints and exception handlers.
    - Register lifecycle hooks for database initialization and disposal.

    The builder keeps construction details isolated so tests can instantiate
    the app with test-specific settings.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build(self) -> Sanic:
        """Construct and return a configured Sanic application instance."""
        configure_logging()
        application = Sanic(self.settings.app.app_name)
        application.config.OAS_UI_REDOC = False
        application.config.OAS_UI_DEFAULT = "swagger"
        application.config.SWAGGER_UI_CONFIGURATION = {"docExpansion": "none"}
        Extend(application)
        application.blueprint(create_api_router(self.settings))
        self._register_exception_handlers(application)
        self._register_lifecycle(application)
        return application

    @staticmethod
    def _register_exception_handlers(application: Sanic) -> None:
        """Register application-wide exception handlers mapping domain errors to HTTP responses."""

        @application.exception(AuthError)
        async def handle_auth_error(_request: Request, exception: AuthError) -> HTTPResponse:
            return error_response(
                status=HTTPStatus.UNAUTHORIZED,
                code="auth_error",
                message=str(exception),
                request=_request,
            )

        @application.exception(NotFoundError)
        async def handle_not_found(_request: Request, exception: NotFoundError) -> HTTPResponse:
            return error_response(
                status=HTTPStatus.NOT_FOUND,
                code="not_found",
                message=str(exception),
                request=_request,
            )

        @application.exception(ConflictError)
        async def handle_conflict(_request: Request, exception: ConflictError) -> HTTPResponse:
            return error_response(
                status=HTTPStatus.CONFLICT,
                code="conflict",
                message=str(exception),
                request=_request,
            )

        @application.exception(ValidationError)
        async def handle_validation(_request: Request, exception: ValidationError) -> HTTPResponse:
            return error_response(
                status=HTTPStatus.BAD_REQUEST,
                code="validation_error",
                message=str(exception),
                request=_request,
            )

    @staticmethod
    def _register_lifecycle(application: Sanic) -> None:
        """Register application lifecycle hooks (start/stop) to manage resources."""

        @application.before_server_start
        async def init_database(app, loop):
            get_database_manager()

        @application.after_server_stop
        async def dispose_database(app, loop):
            await get_database_manager().dispose()
