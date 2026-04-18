from __future__ import annotations

from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


class AppSettings(BaseAppSettings):
    app_name: str = Field(default="PaymentsSanic", validation_alias="APP_NAME")
    environment: str = Field(default="development", validation_alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", validation_alias="APP_HOST")
    app_port: int = Field(default=8000, validation_alias="APP_PORT")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    debug: bool = Field(default=False, validation_alias="DEBUG")


class DatabaseSettings(BaseAppSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://payments:payments@localhost:5432/payments",
        validation_alias="DATABASE_URL",
    )
    migration_database_url: str = Field(
        default="postgresql+psycopg://payments:payments@localhost:5432/payments",
        validation_alias="MIGRATION_DATABASE_URL",
    )


class AuthSettings(BaseAppSettings):
    jwt_secret_key: str = Field(
        default="change-me-jwt-secret-key-at-least-32b",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )


class WebhookSettings(BaseAppSettings):
    secret_key: str = Field(
        default="gfdmhghif38yrf9ew0jkf32", validation_alias="WEBHOOK_SECRET_KEY", min_length=16
    )


class Settings(BaseAppSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    webhook: WebhookSettings = Field(default_factory=WebhookSettings)

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        if self.app.environment.lower() != "production":
            return self

        if self.auth.jwt_secret_key == "change-me-jwt-secret-key-at-least-32b":
            raise ValueError("JWT_SECRET_KEY must be set for production")
        if self.webhook.secret_key == "gfdmhghif38yrf9ew0jkf32":
            raise ValueError("WEBHOOK_SECRET_KEY must be set for production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
