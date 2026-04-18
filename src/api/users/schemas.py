from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.domain.user.role import Role


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role
    created_at: datetime
    updated_at: datetime


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    balance: Decimal
    created_at: datetime
    updated_at: datetime


class UserWithAccountsResponse(UserResponse):
    accounts: list[AccountResponse]


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6, max_length=255)


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=6, max_length=255)
