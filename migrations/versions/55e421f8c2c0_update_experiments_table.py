"""Update experiments table

Revision ID: 55e421f8c2c0
Revises: 746ce4ade43f
Create Date: 2020-04-14 11:51:38.524235

"""
from alembic import op
import sqlalchemy as sa
from app.models import JSONEncodedDict

# revision identifiers, used by Alembic.
revision = '55e421f8c2c0'
down_revision = '746ce4ade43f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('experiment', sa.Column('application', sa.String(length=64), nullable=True))
    op.add_column('experiment', sa.Column('exclusive', sa.Boolean(), nullable=True))
    op.add_column('experiment', sa.Column('parameters', JSONEncodedDict(), nullable=True))
    op.add_column('experiment', sa.Column('scenario', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('experiment', sa.Column('unattended', sa.BOOLEAN(), nullable=True))
    op.drop_column('experiment', 'scenario')
    op.drop_column('experiment', 'parameters')
    op.drop_column('experiment', 'exclusive')
    op.drop_column('experiment', 'automated')
    op.drop_column('experiment', 'application')
    # ### end Alembic commands ###
