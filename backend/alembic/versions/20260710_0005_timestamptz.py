"""make created_at columns timezone-aware

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-10

The app writes timezone-aware datetimes (datetime.now(timezone.utc)) but
these columns were created as TIMESTAMP WITHOUT TIME ZONE. psycopg2 (the
sync driver) silently tolerated the mismatch; asyncpg (adopted for the async
DB access migration) correctly rejects it with a DataError. Fixing the
column type, not the datetimes, since storing timestamps with timezone
awareness is the correct practice Postgres actually supports.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ["users", "api_keys", "translations", "feedback", "datasets", "corrections"]


def upgrade() -> None:
    for table in TABLES:
        op.alter_column(
            table,
            "created_at",
            type_=sa.DateTime(timezone=True),
            existing_type=sa.DateTime(timezone=False),
        )


def downgrade() -> None:
    for table in TABLES:
        op.alter_column(
            table,
            "created_at",
            type_=sa.DateTime(timezone=False),
            existing_type=sa.DateTime(timezone=True),
        )
