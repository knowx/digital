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
        'thing',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_ENGINE='InnoDB',
        mysql_DEFAULT_CHARSET='UTF8'
    )


def downgrade():
    pass
