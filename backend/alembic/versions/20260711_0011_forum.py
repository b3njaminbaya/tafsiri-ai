"""forum_posts and forum_replies tables

Revision ID: 0011
Revises: 0010
Create Date: 2026-07-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "forum_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_forum_posts_id", "forum_posts", ["id"])
    op.create_index("ix_forum_posts_author_id", "forum_posts", ["author_id"])
    op.create_index("ix_forum_posts_category", "forum_posts", ["category"])

    op.create_table(
        "forum_replies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("forum_posts.id"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_forum_replies_id", "forum_replies", ["id"])
    op.create_index("ix_forum_replies_post_id", "forum_replies", ["post_id"])


def downgrade() -> None:
    op.drop_table("forum_replies")
    op.drop_table("forum_posts")
