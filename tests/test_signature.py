from decimal import Decimal

from src.infrastructure.security.signature import build_webhook_signature


def test_build_webhook_signature_matches_example() -> None:
    # Example from the ТЗ: secret_key=gfdmhghif38yrf9ew0jkf32 (default in settings)
    signature = build_webhook_signature(
        account_id=1,
        amount=Decimal("100"),
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        user_id=1,
    )
    assert signature == "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"


def test_build_webhook_signature_different_inputs_produce_different_hashes() -> None:
    sig1 = build_webhook_signature(1, Decimal("100"), "tx-1", 1)
    sig2 = build_webhook_signature(1, Decimal("200"), "tx-1", 1)
    assert sig1 != sig2


def test_build_webhook_signature_decimal_normalization() -> None:
    sig1 = build_webhook_signature(1, Decimal("100"), "tx-1", 1)
    sig2 = build_webhook_signature(1, Decimal("100.00"), "tx-1", 1)
    assert sig1 == sig2
