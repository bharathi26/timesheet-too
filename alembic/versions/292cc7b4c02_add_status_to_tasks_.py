"""Add status to tasks table

Revision ID: 292cc7b4c02
Revises: None
Create Date: 2013-07-25 06:37:21.868493

"""

# revision identifiers, used by Alembic.
revision = '292cc7b4c02'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
            'tasks',
            sa.Column('status', sa.String),
            )


def downgrade():
    op.drop_column( 'tasks', 'status')
