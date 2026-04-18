from __future__ import annotations

from configparser import ConfigParser
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

import src.infrastructure.persistence  # noqa: F401
from alembic import context  # type: ignore[attr-defined]
from src.bootstrap.config import get_settings
from src.infrastructure.db.base import Base

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database.migration_database_url)

if config.config_file_name is not None:
    # Use configparser directly to avoid interpolation issues with logging
    cp = ConfigParser(interpolation=None)
    cp.read(config.config_file_name)
    fileConfig(cp)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=config.get_main_option("sqlalchemy.url"),
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
