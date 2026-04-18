from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class ProcessedPaymentWebhookDTO:
    """DTO returned after handling a payment webhook.

    Contains identifiers of the created payment and account as well as the
    updated account balance.
    """

    payment_id: int
    account_id: int
    balance: Decimal
