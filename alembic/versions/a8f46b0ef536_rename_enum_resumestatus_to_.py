"""rename_enum_resumestatus_to_candidatestatus

Revision ID: a8f46b0ef536
Revises: 43b79754e114
Create Date: 2025-12-07 11:58:35.349883

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8f46b0ef536'
down_revision = '43b79754e114'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename the enum type from 'resumestatus' to 'candidatestatus'
    op.execute("ALTER TYPE resumestatus RENAME TO candidatestatus")


def downgrade() -> None:
    # Rename the enum type back from 'candidatestatus' to 'resumestatus'
    op.execute("ALTER TYPE candidatestatus RENAME TO resumestatus")
