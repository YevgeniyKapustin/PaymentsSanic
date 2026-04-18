from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import mapped_column

Str32 = Annotated[str, 32]
Str64 = Annotated[str, 64]
Str255 = Annotated[str, 255]
MoneyAmount = Annotated[Decimal, "money_amount"]
CreatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    ),
]
UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    ),
]

TYPE_ANNOTATION_MAP = {
    Str32: String(32),
    Str64: String(64),
    Str255: String(255),
    MoneyAmount: Numeric(12, 2),
}
