"""Add remote network services column

Revision ID: 554a80bfdef0
Revises: 6d03b6285416
Create Date: 2020-10-22 09:10:18.603156

"""
from alembic import op
import sqlalchemy as sa
from app.models import JSONEncodedDict


# revision identifiers, used by Alembic.
revision = '554a80bfdef0'
down_revision = '6d03b6285416'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('experiment', sa.Column('remoteNetworkServices', JSONEncodedDict(), nullable=True))


def downgrade():
    op.drop_column('experiment', 'remoteNetworkServices')
