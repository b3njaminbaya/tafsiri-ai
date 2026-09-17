"""security and scale fixes: hashed API keys, token versioning, missing
indexes, and a contact_messages table

Revision ID: 0013
Revises: 0012
Create Date: 2026-09-17

API keys were previously stored (and re-displayed on every list call) as
plaintext. This migration switches to a hashed-at-rest design (see
app/models.py::APIKey and app/security.py::hash_api_key) — any API key
created before this migration stops working and must be recreated, since the
raw value was never retrievable to begin with. There is no real production
data in this project yet, so a clean forward migration (no data-preserving
backfill) is the right tradeoff here.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- API keys: plaintext -> hashed-at-rest ---------------------------
    op.drop_index("ix_api_keys_key", table_name="api_keys")
    op.drop_column("api_keys", "key")
    op.add_column("api_keys", sa.Column("hashed_key", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("api_keys", sa.Column("key_prefix", sa.String(length=12), nullable=False, server_default=""))
    op.create_index("ix_api_keys_hashed_key", "api_keys", ["hashed_key"], unique=True)
    op.alter_column("api_keys", "hashed_key", server_default=None)
    op.alter_column("api_keys", "key_prefix", server_default=None)

    # --- JWT invalidation on password reset/logout -----------------------
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("users", "token_version", server_default=None)

    # --- Missing indexes on hot-path / directly-queried columns -----------
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])
    op.create_index("ix_corrections_reviewer_id", "corrections", ["reviewer_id"])
    op.create_index(
        "ix_glossary_terms_lookup", "glossary_terms", ["domain", "source_lang", "target_lang"]
    )

    # --- Contact form persistence ------------------------------------------
    op.create_table(
        "contact_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_contact_messages_id", "contact_messages", ["id"])
    op.create_index("ix_contact_messages_email", "contact_messages", ["email"])


def downgrade() -> None:
    op.drop_index("ix_contact_messages_email", table_name="contact_messages")
    op.drop_index("ix_contact_messages_id", table_name="contact_messages")
    op.drop_table("contact_messages")

    op.drop_index("ix_glossary_terms_lookup", table_name="glossary_terms")
    op.drop_index("ix_corrections_reviewer_id", table_name="corrections")
    op.drop_index("ix_feedback_user_id", table_name="feedback")

    op.drop_column("users", "token_version")

    op.drop_index("ix_api_keys_hashed_key", table_name="api_keys")
    op.drop_column("api_keys", "key_prefix")
    op.drop_column("api_keys", "hashed_key")
    op.add_column("api_keys", sa.Column("key", sa.String(length=255), nullable=False, server_default=""))
    op.alter_column("api_keys", "key", server_default=None)
    op.create_index("ix_api_keys_key", "api_keys", ["key"], unique=True)
