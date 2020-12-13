"""adding dungeon period

Revision ID: f19eed045826
Revises: d4f2e529527f
Create Date: 2020-12-13 21:40:58.869088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f19eed045826'
down_revision = 'd4f2e529527f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('character_dungeon', sa.Column('dungeon_period', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('character_dungeon', 'dungeon_period')
    # ### end Alembic commands ###