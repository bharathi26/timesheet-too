"""0.5.0 - Add milestones, comment edits, roles, filters

Revision ID: 49c1730a744
Revises: 292cc7b4c02
Create Date: 2013-08-13 12:37:38.422445

"""

# revision identifiers, used by Alembic.
revision = '49c1730a744'
down_revision = '292cc7b4c02'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'milestones',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('desc', sa.String, nullable=False),
        sa.Column('proj_id', sa.String, nullable=False),
        sa.Column('start_date', sa.Date, nullable=True),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('depends_on', sa.Integer, sa.ForeignKey('milestones.id'), nullable=True),
    )

    op.create_table(
        'permissions',
        sa.Column('name', sa.String, primary_key=True),
        sa.Column('user_name', sa.String, sa.ForeignKey('users.username'), primary_key=True),
    )

    op.create_table(
        'filters',
        sa.Column('name', sa.String, primary_key=True),
        sa.Column('user', sa.String, sa.ForeignKey('users.username'), primary_key=True),
        sa.Column('order', sa.Integer),
    )

    op.create_table(
        'comment_edits',
        sa.Column('edit_timestamp', sa.DateTime, server_default=sa.func.now()),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('tasks.id')),
        sa.Column('comment_timestamp', sa.DateTime, sa.ForeignKey('comments.timestamp')),
        sa.Column('text', sa.String),
    )

    op.create_table(
        'statuses',
        sa.Column('name', sa.String, primary_key=True),
        sa.Column('status', sa.String),
        sa.Column('order', sa.Integer),
    )

    op.create_table(
        'priority',
        sa.Column('name', sa.String, primary_key=True),
        sa.Column('order', sa.Integer),
    )

    op.create_table(
        'types',
        sa.Column('name', sa.String, primary_key=True),
        sa.Column('order', sa.Integer),
    )

    op.create_table(
        'areas',
        sa.Column('name', sa.String, primary_key=True),
        sa.Column('order', sa.Integer),
    )

    op.create_table(
        'following',
        sa.Column('username', sa.String, sa.ForeignKey('users.username'), primary_key=True),
        sa.Column('task', sa.Integer, sa.ForeignKey('tasks.id'), primary_key=True),
    )

    op.create_table(
        'attachments',
        sa.Column('filename', sa.String),
        sa.Column('filetype', sa.String),
        sa.Column('data', sa.LargeBinary),
    )


def downgrade():
    op.drop_table('milestones')
    op.drop_table('permissions')
    op.drop_table('filters')
    op.drop_table('comment_edits')
    op.drop_table('statuses')
    op.drop_table('priority')
    op.drop_table('types')
    op.drop_table('areas')
    op.drop_table('following')
    op.drop_table('attachments')

