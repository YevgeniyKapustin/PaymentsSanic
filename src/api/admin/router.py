from http import HTTPStatus

from sanic import Blueprint, HTTPResponse, Request, empty

from src.api.common import parse_payload, response, response_collection
from src.api.dependencies import get_uow
from src.api.users.schemas import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    UserWithAccountsResponse,
)
from src.application.user.mappers import map_user_to_dto
from src.application.user.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    ListUsersWithAccountsUseCase,
    UpdateUserUseCase,
)
from src.auth.dependencies import require_role
from src.domain.user.dto import UserDTO, UserWithAccountsDTO
from src.domain.user.role import Role
from src.infrastructure.db.engine import db_session

router = Blueprint("admin", url_prefix="/admin")


@router.get("/me")
@require_role(Role.ADMIN)
async def get_admin_me(request: Request) -> HTTPResponse:
    user_dto: UserDTO = map_user_to_dto(request.ctx.user)
    return response(UserResponse.model_validate(user_dto))


@router.post("/users")
@require_role(Role.ADMIN)
async def admin_create_user(request: Request) -> HTTPResponse:
    payload = parse_payload(UserCreateRequest, request.json or {})
    if isinstance(payload, HTTPResponse):
        return payload

    async with db_session() as session:
        uow = get_uow(session)
        use_case = CreateUserUseCase(uow)
        user_dto: UserDTO = await use_case.execute(payload)
        return response(UserResponse.model_validate(user_dto), status=HTTPStatus.CREATED)


@router.get("/users")
@require_role(Role.ADMIN)
async def admin_list_users(request: Request) -> HTTPResponse:
    async with db_session() as session:
        uow = get_uow(session)
        use_case = ListUsersWithAccountsUseCase(uow)
        user_dtos: list[UserWithAccountsDTO] = await use_case.execute()
        return response_collection(user_dtos, UserWithAccountsResponse)


@router.put("/users/<user_id:int>")
@require_role(Role.ADMIN)
async def admin_update_user(request: Request, user_id: int) -> HTTPResponse:
    payload = parse_payload(UserUpdateRequest, request.json or {})
    if not isinstance(payload, UserUpdateRequest):
        return payload

    async with db_session() as session:
        uow = get_uow(session)
        use_case = UpdateUserUseCase(uow)
        user_dto: UserDTO = await use_case.execute(user_id, payload)
        return response(UserResponse.model_validate(user_dto))


@router.delete("/users/<user_id:int>")
@require_role(Role.ADMIN)
async def admin_delete_user(request: Request, user_id: int) -> HTTPResponse:
    async with db_session() as session:
        uow = get_uow(session)
        use_case = DeleteUserUseCase(uow)
        await use_case.execute(user_id)
    return empty(status=HTTPStatus.NO_CONTENT)
