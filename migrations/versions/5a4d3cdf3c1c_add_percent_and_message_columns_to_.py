"""Add Percent and Message columns to Execution table

Revision ID: 5a4d3cdf3c1c
Revises: 7ecae5647eb4
Create Date: 2019-05-24 11:23:41.217873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a4d3cdf3c1c'
down_revision = '7ecae5647eb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('execution', sa.Column('message', sa.String(length=128), nullable=True))
    op.add_column('execution', sa.Column('percent', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('execution', 'percent')
    op.drop_column('execution', 'message')
    # ### end Alembic commands ###
