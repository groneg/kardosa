"""add token table

Revision ID: add_token_table
Revises: c847a2a9d9b7
Create Date: 2025-04-21 08:33:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_token_table_uuid'
down_revision = 'c847a2a9d9b7'
branch_labels = None
depends_on = None


def upgrade():
    # Create token table
    op.create_table('token',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expiration', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_token'), 'token', ['token'], unique=True)


def downgrade():
    # Drop token table
    op.drop_index(op.f('ix_token_token'), table_name='token')
    op.drop_table('token')
