"""initial migration

Revision ID: a1b31454e0b0
Revises: None
Create Date: 2016-06-22 15:08:07.873776

"""

# revision identifiers, used by Alembic.
revision = 'a1b31454e0b0'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('modules',
    sa.Column('module_code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('module_code')
    )
    op.create_table('users',
    sa.Column('user_id', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('consultations',
    sa.Column('consult_id', sa.Integer(), nullable=False),
    sa.Column('module_code', sa.String(length=40), nullable=True),
    sa.Column('consult_date', sa.Date(), nullable=True),
    sa.Column('start', sa.Time(), nullable=True),
    sa.Column('end', sa.Time(), nullable=True),
    sa.Column('venue', sa.String(length=40), nullable=True),
    sa.Column('num_of_students', sa.Integer(), nullable=True),
    sa.Column('contact_details', sa.String(length=40), nullable=True),
    sa.Column('teacher_id', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['module_code'], ['modules.module_code'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('consult_id')
    )
    op.create_table('usermodules',
    sa.Column('user_id', sa.String(length=20), nullable=False),
    sa.Column('module_id', sa.String(length=40), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('sem', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['module_id'], ['modules.module_code'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'module_id')
    )
    op.create_table('registrations',
    sa.Column('user_id', sa.String(length=20), nullable=True),
    sa.Column('consult_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['consult_id'], ['consultations.consult_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('registrations')
    op.drop_table('usermodules')
    op.drop_table('consultations')
    op.drop_table('users')
    op.drop_table('modules')
    ### end Alembic commands ###
