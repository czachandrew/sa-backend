"""create partners table

Revision ID: cc196149a123
Revises: 90e0e80c7023
Create Date: 2023-07-19 14:40:38.636422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cc196149a123"
down_revision = "90e0e80c7023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "partners",
        sa.Column(
            "id", sa.Integer(), nullable=False, autoincrement=True, primary_key=True
        ),
        sa.Column("name", sa.String(70), nullable=False),
        sa.Column("api_key", sa.String(100), nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_table("partners")
