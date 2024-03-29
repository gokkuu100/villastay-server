"""removed name from reviews

Revision ID: e2fc35987ab9
Revises: 9a4e20e19263
Create Date: 2024-01-25 10:05:06.837480

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e2fc35987ab9'
down_revision = '9a4e20e19263'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=mysql.MEDIUMBLOB(),
               type_=sa.LargeBinary(length=16277215),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.LargeBinary(length=16277215),
               type_=mysql.MEDIUMBLOB(),
               existing_nullable=True)

    # ### end Alembic commands ###
