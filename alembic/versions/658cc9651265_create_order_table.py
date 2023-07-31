"""create order table

Revision ID: 658cc9651265
Revises: 1edaa0e1f913
Create Date: 2023-07-26 13:08:20.214933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "658cc9651265"
down_revision = "1edaa0e1f913"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column(
            "id", sa.Integer(), nullable=False, autoincrement=True, primary_key=True
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("orders")
