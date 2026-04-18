from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    user_id: int
    account_id: int
    amount: Decimal
    created_at: datetime
    updated_at: datetime


class WebhookRequest(BaseModel):
    transaction_id: str = Field(min_length=1, max_length=255)
    user_id: int
    account_id: int
    amount: Decimal = Field(gt=0)
    signature: str = Field(min_length=64, max_length=64)


class WebhookResponse(BaseModel):
    status: str
    payment_id: int
    account_id: int
    balance: Decimal
