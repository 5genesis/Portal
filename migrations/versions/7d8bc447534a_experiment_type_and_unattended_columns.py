"""Experiment type and unattended columns

Revision ID: 7d8bc447534a
Revises: 2e897fa58901
Create Date: 2019-03-19 12:29:13.545643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d8bc447534a'
down_revision = '2e897fa58901'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('experiment', sa.Column('type', sa.String(length=16), nullable=True))
    op.add_column('experiment', sa.Column('unattended', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('experiment', 'unattended')
    op.drop_column('experiment', 'type')
    # ### end Alembic commands ###
