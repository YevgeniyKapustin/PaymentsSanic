from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class ProcessPaymentWebhookCommand:
    transaction_id: str
    user_id: int
    account_id: int
    amount: Decimal
    signature: str
