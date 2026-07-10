"""translations and feedback tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_lang", sa.String(length=16), nullable=True),
        sa.Column("target_lang", sa.String(length=16), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=True),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_translations_id", "translations", ["id"])
    op.create_index("ix_translations_user_id", "translations", ["user_id"])

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "translation_id", sa.Integer(), sa.ForeignKey("translations.id"), nullable=False
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_feedback_id", "feedback", ["id"])
    op.create_index("ix_feedback_translation_id", "feedback", ["translation_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("translations")
