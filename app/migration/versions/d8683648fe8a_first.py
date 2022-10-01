"""first

Revision ID: d8683648fe8a
Revises: f74781805d62
Create Date: 2022-10-01 17:00:28.910385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8683648fe8a'
down_revision = 'f74781805d62'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title2', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_items_title2'), ['title2'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_items_title2'))
        batch_op.drop_column('title2')

    # ### end Alembic commands ###
