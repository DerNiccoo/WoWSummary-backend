"""prepare gear

Revision ID: 6beb986326bb
Revises: c8e4041daf64
Create Date: 2020-12-12 08:10:32.127946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6beb986326bb'
down_revision = 'c8e4041daf64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('guild_player', sa.Column('gear_score', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('guild_player', 'gear_score')
    # ### end Alembic commands ###
