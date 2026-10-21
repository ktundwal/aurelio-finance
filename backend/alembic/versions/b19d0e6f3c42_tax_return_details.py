"""Preserve detailed retirement, unemployment, and adjustment tax figures.

Revision ID: b19d0e6f3c42
Revises: 7c3b8f4d2a19
"""

from alembic import op
import sqlalchemy as sa


revision = "b19d0e6f3c42"
down_revision = "7c3b8f4d2a19"
branch_labels = None
depends_on = None


_COLUMNS = (
    "retirement_distributions",
    "taxable_retirement_distributions",
    "unemployment_income",
    "hsa_deduction",
    "moving_expenses",
    "ira_deduction",
)


def upgrade() -> None:
    for name in _COLUMNS:
        op.add_column("tax_returns", sa.Column(name, sa.Float(), nullable=True))


def downgrade() -> None:
    for name in reversed(_COLUMNS):
        op.drop_column("tax_returns", name)
