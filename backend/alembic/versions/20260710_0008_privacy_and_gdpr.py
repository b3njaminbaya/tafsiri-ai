"""privacy_settings and gdpr_requests tables

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "privacy_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("analytics", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("marketing", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("functional", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("email_marketing", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("sms_marketing", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("push_notifications", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("data_collection", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("location_tracking", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("third_party_sharing", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_privacy_settings_id", "privacy_settings", ["id"])
    op.create_index("ix_privacy_settings_user_id", "privacy_settings", ["user_id"], unique=True)

    op.create_table(
        "gdpr_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("request_type", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_gdpr_requests_id", "gdpr_requests", ["id"])
    op.create_index("ix_gdpr_requests_user_id", "gdpr_requests", ["user_id"])


def downgrade() -> None:
    op.drop_table("gdpr_requests")
    op.drop_table("privacy_settings")
