"""initial

Revision ID: 6f26a7f5a1c0
Revises: 
Create Date: 2018-04-02 15:09:34.494355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f26a7f5a1c0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'digital_service',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_count', sa.Integer(), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=True),
        sa.Column('binary', sa.String(length=255), nullable=True),
        sa.Column('disabled', sa.Boolean(), nullable=True),
        sa.Column('disabled_reason', sa.String(length=255), nullable=True),
        # 'last_seen_up' has different purpose than 'updated_at'.
        # 'updated_at' refers to any modification of the entry, which can
        # be administrative too, whereas 'last_seen_up' is more related to
        # digital_service. Modeled after nova/servicegroup
        sa.Column('last_seen_up', sa.DateTime(), nullable=True),
        sa.Column('forced_down', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('host', 'binary',
                            name='uniq_digital_service0host0binary')
    )


def downgrade():
    pass
