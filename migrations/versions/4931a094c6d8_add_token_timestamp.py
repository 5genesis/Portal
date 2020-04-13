"""Add token timestamp

Revision ID: 4931a094c6d8
Revises: 29cdef315d5d
Create Date: 2020-03-09 12:43:47.718911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4931a094c6d8'
down_revision = '29cdef315d5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('tokenTimestamp', sa.DATETIME(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'tokenTimestamp')
    # ### end Alembic commands ###