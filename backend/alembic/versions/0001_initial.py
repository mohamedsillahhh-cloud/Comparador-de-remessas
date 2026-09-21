"""tabelas iniciais

Revision ID: 0001
Revises:
Create Date: 2026-09-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("website", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text()),
    )
    op.create_index("ix_providers_slug", "providers", ["slug"], unique=True)

    op.create_table(
        "verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_verifications_provider_id", "verifications", ["provider_id"])

    op.create_table(
        "quote_points",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("verification_id", sa.Integer(), sa.ForeignKey("verifications.id"), nullable=False),
        sa.Column("amount_eur", sa.Numeric(12, 2), nullable=False),
        sa.Column("received_cve", sa.Numeric(14, 2), nullable=False),
        sa.Column("fee_eur", sa.Numeric(12, 2)),
        sa.Column("pct_fee", sa.Numeric(8, 4)),
        sa.Column("fx_rate", sa.Numeric(14, 6)),
        sa.Column("payment_method", sa.String(128)),
        sa.Column("payout_method", sa.String(128)),
        sa.Column("delivery_time", sa.String(128)),
        sa.UniqueConstraint("verification_id", "amount_eur", name="uq_verification_amount"),
        sa.CheckConstraint("amount_eur > 0", name="ck_amount_positive"),
        sa.CheckConstraint("received_cve > 0", name="ck_received_positive"),
    )
    op.create_index("ix_quote_points_verification_id", "quote_points", ["verification_id"])


def downgrade() -> None:
    op.drop_table("quote_points")
    op.drop_table("verifications")
    op.drop_table("providers")