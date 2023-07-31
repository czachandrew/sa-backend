"""expand api_key length

Revision ID: 1edaa0e1f913
Revises: cc196149a123
Create Date: 2023-07-20 13:49:35.549017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1edaa0e1f913"
down_revision = "cc196149a123"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "partners", "api_key", existing_type=sa.String(100), type_=sa.String(255)
    )


def downgrade() -> None:
    op.alter_column(
        "partners", "api_key", existing_type=sa.String(255), type_=sa.String(100)
    )
