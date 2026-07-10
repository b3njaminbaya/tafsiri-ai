"""users.display_name (optional public handle, replaces email-local-part fallback)

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "display_name")
