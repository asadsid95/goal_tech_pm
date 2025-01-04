"""added tag_id in Entry model

Revision ID: 3ddf8eecbb01
Revises: 73c018f0fe52
Create Date: 2025-01-03 20:28:57.518158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ddf8eecbb01'
down_revision = '73c018f0fe52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('entry', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tag_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'tag', ['tag_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('entry', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('tag_id')

    # ### end Alembic commands ###
