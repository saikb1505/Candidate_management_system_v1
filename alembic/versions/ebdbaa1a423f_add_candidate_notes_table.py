"""add candidate_notes table

Revision ID: ebdbaa1a423f
Revises: 266ef93c09ee
Create Date: 2025-12-16 17:19:22.034565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebdbaa1a423f'
down_revision = '266ef93c09ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'candidate_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('previous_status', sa.String(), nullable=True),
        sa.Column('new_status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index(op.f('ix_candidate_notes_id'), 'candidate_notes', ['id'], unique=False)
    op.create_index(op.f('ix_candidate_notes_candidate_id'), 'candidate_notes', ['candidate_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_candidate_notes_candidate_id'), table_name='candidate_notes')
    op.drop_index(op.f('ix_candidate_notes_id'), table_name='candidate_notes')
    op.drop_table('candidate_notes')
