# Backend — NMT Agent API

FastAPI service providing authentication, roles, and API-key management. The
`/translate` endpoint is currently a placeholder pending integration with
`ml-service` (see [../docs/AUDIT.md](../docs/AUDIT.md)).

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Set `DATABASE_URL` (defaults to `postgresql+psycopg2://postgres:postgres@localhost:5432/nmt`)
and `SECRET_KEY` as needed — see `app/core/config.py` for all settings.

## Migrations (Alembic)

Schema is managed by Alembic; there is no `create_all()` bootstrap anymore.

```bash
alembic upgrade head            # apply all migrations
alembic revision -m "message"   # create a new empty migration
```

When you change a model in `app/models.py`, write a matching migration under
`alembic/versions/` (autogeneration works too if you have a live DB configured:
`alembic revision --autogenerate -m "message"`, then review the diff before applying).

The `docker-compose` backend service runs `alembic upgrade head` automatically
before starting uvicorn.

## Tests

```bash
pytest
```

Tests use an isolated SQLite database (see `tests/conftest.py`) so they don't
touch your local Postgres instance.
