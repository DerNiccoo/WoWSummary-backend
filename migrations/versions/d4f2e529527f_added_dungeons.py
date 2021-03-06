"""added dungeons

Revision ID: d4f2e529527f
Revises: b29f3f891ee1
Create Date: 2020-12-13 21:29:02.801093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4f2e529527f'
down_revision = 'b29f3f891ee1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('character_dungeon',
    sa.Column('dungeon_id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('intime', sa.Boolean(), nullable=True),
    sa.Column('dungeon', sa.String(length=32), nullable=True),
    sa.Column('keystone_level', sa.Integer(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['guild_player.player_id'], ),
    sa.PrimaryKeyConstraint('dungeon_id', 'player_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('character_dungeon')
    # ### end Alembic commands ###
