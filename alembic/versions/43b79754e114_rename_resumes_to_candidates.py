"""rename_resumes_to_candidates

Revision ID: 43b79754e114
Revises: 88291e228a10
Create Date: 2025-11-27 23:00:46.797830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43b79754e114'
down_revision = '88291e228a10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename the table
    op.rename_table('resumes', 'candidates')

    # Rename the columns
    op.alter_column('candidates', 'candidate_name', new_column_name='name')
    op.alter_column('candidates', 'candidate_email', new_column_name='email')
    op.alter_column('candidates', 'candidate_phone', new_column_name='phone')

    # Rename the index
    op.drop_index('ix_resumes_candidate_email', table_name='candidates')
    op.create_index('ix_candidates_email', 'candidates', ['email'])

    op.drop_index('ix_resumes_id', table_name='candidates')
    op.create_index('ix_candidates_id', 'candidates', ['id'])


def downgrade() -> None:
    # Rename the table back
    op.rename_table('candidates', 'resumes')

    # Rename the columns back
    op.alter_column('resumes', 'name', new_column_name='candidate_name')
    op.alter_column('resumes', 'email', new_column_name='candidate_email')
    op.alter_column('resumes', 'phone', new_column_name='candidate_phone')

    # Rename the index back
    op.drop_index('ix_candidates_email', table_name='resumes')
    op.create_index('ix_resumes_candidate_email', 'resumes', ['candidate_email'])

    op.drop_index('ix_candidates_id', table_name='resumes')
    op.create_index('ix_resumes_id', 'resumes', ['id'])
