"""datasets table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_lang", sa.String(length=16), nullable=True),
        sa.Column("target_lang", sa.String(length=16), nullable=True),
        sa.Column("domain", sa.String(length=32), nullable=True),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_datasets_id", "datasets", ["id"])


def downgrade() -> None:
    op.drop_table("datasets")
