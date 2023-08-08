"""added cascading delete between orders and orderitems

Revision ID: 96ea5ec2d696
Revises: 02f71845ed4a
Create Date: 2023-08-08 15:21:46.096724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "96ea5ec2d696"
down_revision = "02f71845ed4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing foreign key constraint if it exists
    op.drop_constraint("order_items_order_id_fkey", "order_items", type_="foreignkey")

    # Add the new foreign key constraint with ondelete='CASCADE'
    op.create_foreign_key(
        "order_items_order_id_fkey",
        "order_items",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Drop the cascade foreign key constraint
    op.drop_constraint("order_items_order_id_fkey", "order_items", type_="foreignkey")

    # Re-add the original foreign key constraint without cascade
    op.create_foreign_key(
        "order_items_order_id_fkey", "order_items", "orders", ["order_id"], ["id"]
    )
