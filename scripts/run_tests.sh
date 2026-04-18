#!/usr/bin/env bash
set -e

docker compose run --rm \
  -v "$(pwd)/tests:/app/tests" \
  app sh -c "pip install --quiet 'pytest==8.3.5' 'pytest-asyncio==0.26.0' 'aiosqlite>=0.21.0' && pytest tests/ -v $*"
