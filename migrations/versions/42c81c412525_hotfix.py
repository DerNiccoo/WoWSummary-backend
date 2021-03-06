"""hotfix

Revision ID: 42c81c412525
Revises: 6beb986326bb
Create Date: 2020-12-12 08:34:54.865249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42c81c412525'
down_revision = '6beb986326bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guild',
    sa.Column('guild_id', sa.Integer(), nullable=False),
    sa.Column('realm', sa.String(length=32), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('faction', sa.String(length=16), nullable=True),
    sa.Column('last_modified', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('guild_id'),
    sa.UniqueConstraint('guild_id')
    )
    op.create_index(op.f('ix_guild_name'), 'guild', ['name'], unique=False)
    op.create_table('guild_player',
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('guild_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('playable_class', sa.String(length=32), nullable=True),
    sa.Column('race', sa.String(length=32), nullable=True),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('last_modified', sa.Integer(), nullable=True),
    sa.Column('gear_score', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guild.guild_id'], ),
    sa.PrimaryKeyConstraint('player_id'),
    sa.UniqueConstraint('player_id', 'guild_id')
    )
    op.create_index(op.f('ix_guild_player_name'), 'guild_player', ['name'], unique=False)
    op.create_table('character_equipment',
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('slot', sa.String(length=32), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('itemClass', sa.String(length=32), nullable=True),
    sa.Column('itemSubclass', sa.String(length=32), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('quality', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['guild_player.player_id'], ),
    sa.PrimaryKeyConstraint('item_id', 'slot', 'player_id'),
    sa.UniqueConstraint('item_id', 'slot', 'player_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('character_equipment')
    op.drop_index(op.f('ix_guild_player_name'), table_name='guild_player')
    op.drop_table('guild_player')
    op.drop_index(op.f('ix_guild_name'), table_name='guild')
    op.drop_table('guild')
    # ### end Alembic commands ###
