"""convert_enums_to_varchar

Revision ID: d5e8f9a1b2c3
Revises: c4bf82546c55
Create Date: 2025-12-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'd5e8f9a1b2c3'
down_revision = 'c4bf82546c55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Converts ENUM columns to VARCHAR(50) for both candidates.status and users.role.
    This provides more flexibility for future status/role values without requiring
    database-level enum modifications.
    """
    connection = op.get_bind()

    # Step 1: Convert candidates.status from ENUM to VARCHAR(50)
    print("Converting candidates.status from ENUM to VARCHAR(50)...")

    # Drop the default constraint
    op.execute("ALTER TABLE candidates ALTER COLUMN status DROP DEFAULT")

    # Convert the column to VARCHAR
    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN status TYPE VARCHAR(50)
        USING (status::text)
    """)

    # Re-add the default constraint with VARCHAR
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'uploaded'")

    # Drop the old candidatestatus enum type if it exists
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'candidatestatus'
        )
    """))
    if result.scalar():
        op.execute("DROP TYPE candidatestatus")
        print("Dropped candidatestatus ENUM type")

    print("Converted candidates.status to VARCHAR(50)")

    # Step 2: Convert users.role from ENUM to VARCHAR(50)
    print("Converting users.role from ENUM to VARCHAR(50)...")

    # Check if userrole enum exists
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'userrole'
        )
    """))
    userrole_enum_exists = result.scalar()

    if userrole_enum_exists:
        # Drop the default constraint
        op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")

        # Convert the column to VARCHAR
        op.execute("""
            ALTER TABLE users
            ALTER COLUMN role TYPE VARCHAR(50)
            USING (role::text)
        """)

        # Re-add the default constraint with VARCHAR
        op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'viewer'")

        # Drop the old userrole enum type
        op.execute("DROP TYPE userrole")
        print("Dropped userrole ENUM type")
    else:
        # If enum doesn't exist, just ensure the column is VARCHAR
        op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
        op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50)")
        op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'viewer'")

    print("Converted users.role to VARCHAR(50)")
    print("Migration completed successfully!")


def downgrade() -> None:
    """
    Reverts VARCHAR columns back to ENUM types.
    Note: This will fail if any values exist that aren't in the ENUM definition.
    """
    print("Converting back to ENUM types...")

    # Recreate candidatestatus ENUM
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

    # Convert candidates.status back to ENUM
    op.execute("ALTER TABLE candidates ALTER COLUMN status DROP DEFAULT")
    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN status TYPE candidatestatus
        USING (status::text::candidatestatus)
    """)
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'uploaded'::candidatestatus")

    # Recreate userrole ENUM
    op.execute("""
        CREATE TYPE userrole AS ENUM (
            'admin',
            'hr_manager',
            'recruiter',
            'viewer'
        )
    """)

    # Convert users.role back to ENUM
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role TYPE userrole
        USING (role::text::userrole)
    """)
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'viewer'::userrole")

    print("Downgrade completed successfully!")
