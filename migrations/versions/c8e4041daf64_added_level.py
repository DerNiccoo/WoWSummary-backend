"""added level

Revision ID: c8e4041daf64
Revises: d3afce3ef9ef
Create Date: 2020-12-11 15:21:46.591462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8e4041daf64'
down_revision = 'd3afce3ef9ef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('guild_player', sa.Column('level', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('guild_player', 'level')
    # ### end Alembic commands ###
