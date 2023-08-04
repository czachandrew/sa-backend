"""Add status to inventory

Revision ID: 02f71845ed4a
Revises: f4100a3b1d65
Create Date: 2023-08-04 11:26:35.773067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "02f71845ed4a"
down_revision = "f4100a3b1d65"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory", sa.Column("status", sa.String(255), default="good"))


def downgrade() -> None:
    op.drop_column("inventory", "status")
