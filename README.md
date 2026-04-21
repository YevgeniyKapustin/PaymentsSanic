# PaymentsSanic

Asynchronous REST API for user, account, and payment management.

Tech stack: `Sanic`, `SQLAlchemy`, `PostgreSQL`, `Alembic`, and `Poetry`.

## Features

- User and admin authentication with `email/password`
- JWT-based authorization for protected endpoints
- User profile, account list, and payment history endpoints
- Admin CRUD operations for users
- Payment webhook processing with signature validation
- Idempotent webhook handling for duplicate `transaction_id`

## Project Structure

```text
src/
├── api/              # HTTP routes and request/response schemas
├── application/      # Use cases, ports, and commands
├── auth/             # Auth dependencies and role guards
├── bootstrap/        # App bootstrap and configuration
├── domain/           # Domain DTOs and enums
├── infrastructure/   # DB, repositories, and security utilities
├── shared/           # Shared exceptions
└── main.py           # Application entrypoint
```

## Run with Docker Compose

```bash
docker compose up --build
```

- API will be available at http://localhost:8000.

## Run Locally

1. Create a PostgreSQL database named `payments`.
2. Copy `.env.example` to `.env` and adjust values if needed.
3. Install dependencies.
4. Apply migrations.
5. Start the application.

```bash
copy .env.example .env
poetry install
poetry run alembic upgrade head
poetry run python run.py
```

## Tests and Linters

Install dev dependencies:

```bash
poetry install --with dev
```

Run checks:

```bash
poetry run ruff check
poetry run black --check .
poetry run isort --check-only .
poetry run mypy .
poetry run bandit -r src
poetry run pytest --cov
```

## Main API Routes

- `POST /api/v1/auth/user/login`
- `POST /api/v1/auth/admin/login`
- `GET /api/v1/users/me`
- `GET /api/v1/users/me/accounts`
- `GET /api/v1/users/me/payments`
- `GET /api/v1/admin/me`
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users`
- `PUT /api/v1/admin/users/{user_id}`
- `DELETE /api/v1/admin/users/{user_id}`
- `POST /api/v1/webhooks/payments`

## Webhook Payload Example

```json
{
  "transaction_id": "tx_001",
  "user_id": 1,
  "account_id": 10,
  "amount": 150,
  "signature": "4ff5c81fa28ad74f8bdaea652405d773ad0cde5d6f0fd27100f8421885397b38"
}
```

Admin
```
email: admin@example.com
password: admin123
role: ADMIN
```

User
```
email: user@example.com
password: user123
role: USER
```
