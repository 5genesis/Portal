"""Add column DasboardUrl to Execution table

Revision ID: 7ecae5647eb4
Revises: 01a9a57a22c5
Create Date: 2019-05-23 11:05:36.498013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ecae5647eb4'
down_revision = '01a9a57a22c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('execution', sa.Column('dashboard_url', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('execution', 'dashboard_url')
    # ### end Alembic commands ###
