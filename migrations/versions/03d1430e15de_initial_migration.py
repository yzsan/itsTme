"""Initial migration

Revision ID: 03d1430e15de
Revises: 
Create Date: 2024-08-04 18:10:00.824640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03d1430e15de'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('update')
    op.drop_table('activity')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activity',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=200), nullable=False),
    sa.Column('last_done', sa.DATETIME(), nullable=True),
    sa.Column('details', sa.VARCHAR(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('update',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('activity_id', sa.INTEGER(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('note', sa.VARCHAR(length=500), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['activity.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
