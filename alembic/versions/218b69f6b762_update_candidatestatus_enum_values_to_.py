"""update_candidatestatus_enum_values_to_lowercase

Revision ID: 218b69f6b762
Revises: a8f46b0ef536
Create Date: 2025-12-07 12:32:49.089482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '218b69f6b762'
down_revision = 'a8f46b0ef536'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a new enum type with lowercase values
    op.execute("CREATE TYPE candidatestatus_new AS ENUM ('uploaded', 'processing', 'completed', 'failed')")

    # Drop the default constraint temporarily
    op.execute("ALTER TABLE candidates ALTER COLUMN status DROP DEFAULT")

    # Update existing data to lowercase
    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN status TYPE candidatestatus_new
        USING (LOWER(status::text)::candidatestatus_new)
    """)

    # Drop the old enum type
    op.execute("DROP TYPE candidatestatus")

    # Rename the new enum type to the original name
    op.execute("ALTER TYPE candidatestatus_new RENAME TO candidatestatus")

    # Re-add the default constraint with lowercase value
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'uploaded'::candidatestatus")


def downgrade() -> None:
    # Create a new enum type with uppercase values
    op.execute("CREATE TYPE candidatestatus_new AS ENUM ('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED')")

    # Drop the default constraint temporarily
    op.execute("ALTER TABLE candidates ALTER COLUMN status DROP DEFAULT")

    # Update existing data to uppercase
    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN status TYPE candidatestatus_new
        USING (UPPER(status::text)::candidatestatus_new)
    """)

    # Drop the old enum type
    op.execute("DROP TYPE candidatestatus")

    # Rename the new enum type to the original name
    op.execute("ALTER TYPE candidatestatus_new RENAME TO candidatestatus")

    # Re-add the default constraint with uppercase value
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'UPLOADED'::candidatestatus")
