"""Record VIM name on network service

Revision ID: 56345866eed9
Revises: 554a80bfdef0
Create Date: 2021-07-13 12:10:20.999983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56345866eed9'
down_revision = '554a80bfdef0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('network_service', sa.Column('vim_name', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('network_service', 'vim_name')
    # ### end Alembic commands ###