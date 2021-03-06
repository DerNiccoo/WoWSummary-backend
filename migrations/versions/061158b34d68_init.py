"""init

Revision ID: 061158b34d68
Revises: 
Create Date: 2020-12-10 21:06:54.607133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '061158b34d68'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guild',
    sa.Column('guild_id', sa.Integer(), nullable=False),
    sa.Column('realm', sa.String(length=32), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('faction', sa.String(length=16), nullable=True),
    sa.PrimaryKeyConstraint('guild_id')
    )
    op.create_index(op.f('ix_guild_name'), 'guild', ['name'], unique=False)
    op.create_table('guild_player',
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('guild_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('playable_class', sa.String(length=32), nullable=True),
    sa.Column('race', sa.String(length=32), nullable=True),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('character_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guild.guild_id'], ),
    sa.PrimaryKeyConstraint('player_id', 'guild_id')
    )
    op.create_index(op.f('ix_guild_player_name'), 'guild_player', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_guild_player_name'), table_name='guild_player')
    op.drop_table('guild_player')
    op.drop_index(op.f('ix_guild_name'), table_name='guild')
    op.drop_table('guild')
    # ### end Alembic commands ###
