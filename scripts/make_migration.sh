#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./make_migration.sh <migration_message>"
  exit 1
fi

docker compose run --rm migrator alembic revision --autogenerate -m "$1"
