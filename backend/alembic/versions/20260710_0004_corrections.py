"""corrections table (active-learning review queue)

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "corrections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "translation_id", sa.Integer(), sa.ForeignKey("translations.id"), nullable=False
        ),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_corrections_id", "corrections", ["id"])
    op.create_index("ix_corrections_translation_id", "corrections", ["translation_id"])


def downgrade() -> None:
    op.drop_table("corrections")
