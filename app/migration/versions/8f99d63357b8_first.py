"""first

Revision ID: 8f99d63357b8
Revises: d8683648fe8a
Create Date: 2022-10-01 17:02:01.148171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f99d63357b8'
down_revision = 'd8683648fe8a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_index('ix_items_title2')
        batch_op.drop_column('title2')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title2', sa.VARCHAR(), nullable=True))
        batch_op.create_index('ix_items_title2', ['title2'], unique=False)

    # ### end Alembic commands ###
