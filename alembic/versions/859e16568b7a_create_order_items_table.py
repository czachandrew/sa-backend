"""create order items table

Revision ID: 859e16568b7a
Revises: 658cc9651265
Create Date: 2023-07-26 13:12:46.873127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "859e16568b7a"
down_revision = "658cc9651265"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "order_items",
        sa.Column(
            "id", sa.Integer(), nullable=False, autoincrement=True, primary_key=True
        ),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("inventory_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("order_items")
