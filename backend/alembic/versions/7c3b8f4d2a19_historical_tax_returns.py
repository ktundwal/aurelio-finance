"""Store annual historical tax returns.

Revision ID: 7c3b8f4d2a19
Revises: 1f24a6148f6b
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "7c3b8f4d2a19"
down_revision = "1f24a6148f6b"
branch_labels = None
depends_on = None


_AMOUNT_COLUMNS = (
    "wages",
    "taxable_interest",
    "tax_exempt_interest",
    "ordinary_dividends",
    "qualified_dividends",
    "capital_gain",
    "business_income",
    "other_income",
    "total_income",
    "adjustments",
    "adjusted_gross_income",
    "deductions",
    "exemptions",
    "taxable_income",
    "tax_before_credits",
    "credits",
    "other_taxes",
    "total_tax",
    "withholding",
    "estimated_payments",
    "other_payments",
    "total_payments",
    "refund",
    "amount_owed",
    "penalty",
)


def upgrade() -> None:
    columns = [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tax_year", sa.Integer(), nullable=False),
        sa.Column("jurisdiction", sa.String(), nullable=False),
        sa.Column("filing_status", sa.String(), nullable=True),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("coverage", sa.String(), nullable=False),
    ]
    columns.extend(sa.Column(name, sa.Float(), nullable=True) for name in _AMOUNT_COLUMNS)
    columns.extend(
        [
            sa.Column("source_path", sa.Text(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.String(), nullable=False),
            sa.UniqueConstraint(
                "tax_year", "jurisdiction", name="uq_tax_return_year_jurisdiction"
            ),
        ]
    )
    op.create_table("tax_returns", *columns)
    op.create_index("ix_tax_returns_tax_year", "tax_returns", ["tax_year"])


def downgrade() -> None:
    op.drop_index("ix_tax_returns_tax_year", table_name="tax_returns")
    op.drop_table("tax_returns")
