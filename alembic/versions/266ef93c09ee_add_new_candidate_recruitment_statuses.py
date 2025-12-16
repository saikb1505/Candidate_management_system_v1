"""add_new_candidate_recruitment_statuses

Revision ID: 266ef93c09ee
Revises: 46d35f0707f9
Create Date: 2025-12-16 15:33:00.906261

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '266ef93c09ee'
down_revision = '46d35f0707f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL doesn't allow adding enum values in a transaction.
    # We recreate the enum type with all values (old + new)

    # Create a new enum type with all values
    op.execute("""
        CREATE TYPE candidatestatus_new AS ENUM (
            'uploaded',
            'processing',
            'completed',
            'failed',
            'reviewing',
            'callback_requested',
            'initial_screening_completed',
            'interview_scheduled',
            'selected',
            'rejected'
        )
    """)

    # Drop the default constraint temporarily
    op.execute("ALTER TABLE candidates ALTER COLUMN status DROP DEFAULT")

    # Alter the column to use the new enum type
    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN status TYPE candidatestatus_new
        USING (status::text::candidatestatus_new)
    """)

    # Drop the old enum type
    op.execute("DROP TYPE candidatestatus")

    # Rename the new enum type to the original name
    op.execute("ALTER TYPE candidatestatus_new RENAME TO candidatestatus")

    # Re-add the default constraint
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'uploaded'::candidatestatus")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly
    # To downgrade, you would need to:
    # 1. Create a new enum without the new values
    # 2. Migrate data to use only old values
    # 3. Alter the column to use the new enum
    # 4. Drop the old enum and rename the new one

    # For safety, we'll create a new enum with only the original values
    op.execute("CREATE TYPE candidatestatus_old AS ENUM ('uploaded', 'processing', 'completed', 'failed')")

    # Drop the default constraint temporarily
    op.execute("ALTER TABLE candidates ALTER COLUMN status DROP DEFAULT")

    # Update any records using new statuses to a safe default (e.g., 'uploaded')
    op.execute("""
        UPDATE candidates
        SET status = 'uploaded'
        WHERE status NOT IN ('uploaded', 'processing', 'completed', 'failed')
    """)

    # Alter the column to use the old enum
    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN status TYPE candidatestatus_old
        USING (status::text::candidatestatus_old)
    """)

    # Drop the new enum type
    op.execute("DROP TYPE candidatestatus")

    # Rename the old enum type back to candidatestatus
    op.execute("ALTER TYPE candidatestatus_old RENAME TO candidatestatus")

    # Re-add the default constraint
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'uploaded'::candidatestatus")
