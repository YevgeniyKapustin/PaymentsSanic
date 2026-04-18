from sanic import Blueprint, HTTPResponse, Request

from src.api.auth.schemas import LoginRequest, TokenResponse
from src.api.common import parse_payload, response
from src.api.dependencies import get_user_repository
from src.application.auth.use_cases import AuthenticateUserUseCase
from src.infrastructure.db.engine import db_session

router = Blueprint("auth", url_prefix="/auth")


@router.post("/login")
async def login(request: Request) -> HTTPResponse:
    payload = parse_payload(LoginRequest, request.json or {})
    if isinstance(payload, HTTPResponse):
        return payload

    async with db_session() as session:
        repo = get_user_repository(session)
        use_case = AuthenticateUserUseCase(repo)
        auth_dto = await use_case.execute(payload.email, payload.password)
        return response(TokenResponse(access_token=auth_dto.access_token))
