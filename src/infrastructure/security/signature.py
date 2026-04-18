import hashlib
from decimal import Decimal

from src.bootstrap.config import get_settings


def build_webhook_signature(
    account_id: int, amount: Decimal, transaction_id: str, user_id: int
) -> str:
    settings = get_settings()
    normalized_amount = (
        format(amount, "f").rstrip("0").rstrip(".")
        if "." in format(amount, "f")
        else format(amount, "f")
    )
    raw = f"{account_id}{normalized_amount}{transaction_id}{user_id}{settings.webhook.secret_key}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
