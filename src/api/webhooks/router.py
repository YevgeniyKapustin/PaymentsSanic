from sanic import Blueprint, HTTPResponse, Request

from src.api.common import parse_payload, response
from src.api.dependencies import get_uow
from src.api.webhooks.schemas import WebhookRequest, WebhookResponse
from src.application.payment.commands import ProcessPaymentWebhookCommand
from src.application.payment.use_cases import ProcessPaymentWebhookUseCase
from src.domain.payment.dto import ProcessedPaymentWebhookDTO
from src.infrastructure.db.engine import db_session

router = Blueprint("webhooks", url_prefix="/webhooks")


@router.post("/payments")
async def payment_webhook(request: Request) -> HTTPResponse:
    payload: WebhookRequest | HTTPResponse = parse_payload(WebhookRequest, request.json or {})
    if isinstance(payload, HTTPResponse):
        return payload

    async with db_session() as session:
        uow = get_uow(session)
        use_case = ProcessPaymentWebhookUseCase(uow)
        result: ProcessedPaymentWebhookDTO = await use_case.execute(
            ProcessPaymentWebhookCommand(
                transaction_id=payload.transaction_id,
                user_id=payload.user_id,
                account_id=payload.account_id,
                amount=payload.amount,
                signature=payload.signature,
            ),
        )
        return response(
            WebhookResponse(
                status="processed",
                payment_id=result.payment_id,
                account_id=result.account_id,
                balance=result.balance,
            )
        )
