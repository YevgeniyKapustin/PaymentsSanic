from sanic import Blueprint, HTTPResponse, Request

from src.api.common import response, response_collection
from src.api.dependencies import get_uow
from src.api.users.schemas import AccountResponse, UserResponse
from src.api.webhooks.schemas import PaymentResponse
from src.application.user.mappers import map_user_to_dto
from src.application.user.use_cases import (
    GetUserAccountsUseCase,
    GetUserPaymentsUseCase,
)
from src.auth.dependencies import require_role
from src.domain.user.dto import AccountDTO, PaymentDTO, UserDTO
from src.domain.user.role import Role
from src.infrastructure.db.engine import db_session

router = Blueprint("users", url_prefix="/users")


@router.get("/me")
@require_role(Role.USER)
async def get_me(request: Request) -> HTTPResponse:
    user_dto: UserDTO = map_user_to_dto(request.ctx.user)
    return response(UserResponse.model_validate(user_dto))


@router.get("/me/accounts")
@require_role(Role.USER)
async def get_my_accounts(request: Request) -> HTTPResponse:
    async with db_session() as session:
        uow = get_uow(session)
        use_case = GetUserAccountsUseCase(uow)
        accounts: list[AccountDTO] = await use_case.execute(request.ctx.user.id)
        return response_collection(accounts, AccountResponse)


@router.get("/me/payments")
@require_role(Role.USER)
async def get_my_payments(request: Request) -> HTTPResponse:
    async with db_session() as session:
        uow = get_uow(session)
        use_case = GetUserPaymentsUseCase(uow)
        payments: list[PaymentDTO] = await use_case.execute(request.ctx.user.id)
        return response_collection(payments, PaymentResponse)
