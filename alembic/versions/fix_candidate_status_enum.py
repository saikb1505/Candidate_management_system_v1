"""fix_candidate_status_enum

Revision ID: fix_candidate_status
Revises: 43b79754e114
Create Date: 2025-12-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_candidate_status'
down_revision = '43b79754e114'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Create the new enum type with lowercase values
    op.execute("CREATE TYPE candidatestatus AS ENUM ('uploaded', 'processing', 'completed', 'failed')")

    # Step 2: Add a temporary column with the new enum type
    op.add_column('candidates', sa.Column('status_new', sa.Enum('uploaded', 'processing', 'completed', 'failed', name='candidatestatus'), nullable=True))

    # Step 3: Copy data from old column to new column, converting uppercase to lowercase
    op.execute("""
        UPDATE candidates
        SET status_new = CASE
            WHEN status::text = 'UPLOADED' THEN 'uploaded'::candidatestatus
            WHEN status::text = 'PROCESSING' THEN 'processing'::candidatestatus
            WHEN status::text = 'COMPLETED' THEN 'completed'::candidatestatus
            WHEN status::text = 'FAILED' THEN 'failed'::candidatestatus
        END
    """)

    # Step 4: Drop the old column
    op.drop_column('candidates', 'status')

    # Step 5: Rename the new column to 'status'
    op.alter_column('candidates', 'status_new', new_column_name='status')

    # Step 6: Make the column non-nullable and set default
    op.alter_column('candidates', 'status', nullable=False)
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'uploaded'::candidatestatus")

    # Step 7: Drop the old enum type
    op.execute("DROP TYPE resumestatus")


def downgrade() -> None:
    # Step 1: Create the old enum type
    op.execute("CREATE TYPE resumestatus AS ENUM ('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED')")

    # Step 2: Add a temporary column with the old enum type
    op.add_column('candidates', sa.Column('status_old', sa.Enum('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED', name='resumestatus'), nullable=True))

    # Step 3: Copy data from new column to old column, converting lowercase to uppercase
    op.execute("""
        UPDATE candidates
        SET status_old = CASE
            WHEN status::text = 'uploaded' THEN 'UPLOADED'::resumestatus
            WHEN status::text = 'processing' THEN 'PROCESSING'::resumestatus
            WHEN status::text = 'completed' THEN 'COMPLETED'::resumestatus
            WHEN status::text = 'failed' THEN 'FAILED'::resumestatus
        END
    """)

    # Step 4: Drop the new column
    op.drop_column('candidates', 'status')

    # Step 5: Rename the old column to 'status'
    op.alter_column('candidates', 'status_old', new_column_name='status')

    # Step 6: Make the column non-nullable and set default
    op.alter_column('candidates', 'status', nullable=False)
    op.execute("ALTER TABLE candidates ALTER COLUMN status SET DEFAULT 'UPLOADED'::resumestatus")

    # Step 7: Drop the new enum type
    op.execute("DROP TYPE candidatestatus")
