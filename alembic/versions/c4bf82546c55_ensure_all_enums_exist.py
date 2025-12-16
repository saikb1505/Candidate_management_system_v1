"""ensure_all_enums_exist

Revision ID: c4bf82546c55
Revises: ebdbaa1a423f
Create Date: 2025-12-16 19:00:17.718267

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'c4bf82546c55'
down_revision = 'ebdbaa1a423f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Ensures the candidatestatus ENUM has all required values.
    This migration is idempotent - it checks if the enum exists and recreates it
    with all values if needed, or verifies it has all values if it already exists.
    """

    connection = op.get_bind()

    # Check if candidatestatus enum type exists
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'candidatestatus'
        )
    """))
    enum_exists = result.scalar()

    if enum_exists:
        # Get current enum values
        result = connection.execute(text("""
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'candidatestatus'
            ORDER BY e.enumlabel
        """))
        existing_values = {row[0] for row in result}

        # Define all required values
        required_values = {
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
        }

        # Check if we need to update the enum
        if not required_values.issubset(existing_values):
            print(f"Updating candidatestatus enum. Current values: {existing_values}")
            print(f"Required values: {required_values}")

            # Recreate enum with all values
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

            print("candidatestatus enum updated successfully")
        else:
            print(f"candidatestatus enum already has all required values: {existing_values}")
    else:
        # Create the enum from scratch
        print("Creating candidatestatus enum")
        op.execute("""
            CREATE TYPE candidatestatus AS ENUM (
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
        print("candidatestatus enum created successfully")


def downgrade() -> None:
    """
    Downgrade is not supported as it would require data migration.
    To rollback, you would need to manually handle any data using the new enum values.
    """
    pass
