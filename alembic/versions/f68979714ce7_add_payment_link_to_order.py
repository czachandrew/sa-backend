"""Add payment link to order

Revision ID: f68979714ce7
Revises: 96ea5ec2d696
Create Date: 2023-08-28 12:10:24.048698

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f68979714ce7"
down_revision = "96ea5ec2d696"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "orders",
        sa.Column("payment_link", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("orders", "payment_link")
    # ### end Alembic commands ###
