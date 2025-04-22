"""merge heads for V1 production

Revision ID: 0caf70949dca
Revises: 036c0cc04463, add_token_table_uuid
Create Date: 2025-04-21 21:34:51.176402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0caf70949dca'
down_revision = ('036c0cc04463', 'add_token_table_uuid')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
