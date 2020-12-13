"""added gear ench

Revision ID: 7fb4426605a8
Revises: 54c228e72d50
Create Date: 2020-12-12 21:58:52.651230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fb4426605a8'
down_revision = '54c228e72d50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('character_equipment', sa.Column('enchantments', sa.Integer(), nullable=True))
    op.add_column('character_equipment', sa.Column('socket', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('character_equipment', 'socket')
    op.drop_column('character_equipment', 'enchantments')
    # ### end Alembic commands ###
