"""create user table

Revision ID: 90e0e80c7023
Revises: dc1f54d391dd
Create Date: 2023-07-18 11:47:04.339323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "90e0e80c7023"
down_revision = "dc1f54d391dd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id", sa.Integer(), nullable=False, autoincrement=True, primary_key=True
        ),
        sa.Column("email", sa.String(70), nullable=False),
        sa.Column("hashed_password", sa.String(100), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("users")
