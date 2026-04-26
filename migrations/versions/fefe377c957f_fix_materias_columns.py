"""fix materias columns

Revision ID: fefe377c957f
Revises: aba1da756837
Create Date: 2026-04-26 18:00:55.428650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fefe377c957f'
down_revision = 'aba1da756837'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Remove tabela temporária travada se ainda existir
    if conn.dialect.has_table(conn, '_alembic_tmp_materias'):
        op.drop_table('_alembic_tmp_materias')

    # Recria materias do zero trocando id_professor/id_turma por professor_id/turma_id
    with op.batch_alter_table('materias', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('professor_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('turma_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_materia_turma', 'turmas', ['turma_id'], ['id'])
        batch_op.create_foreign_key('fk_materia_professor', 'professor', ['professor_id'], ['id'])
        batch_op.drop_column('id_turma')
        batch_op.drop_column('id_professor')

    with op.batch_alter_table('professor', schema=None, recreate='always') as batch_op:
        batch_op.create_unique_constraint('uq_professor_email', ['email'])

    with op.batch_alter_table('secretaria', schema=None, recreate='always') as batch_op:
        batch_op.create_unique_constraint('uq_secretaria_email', ['email'])

    with op.batch_alter_table('turmas', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('data_inicio', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('data_final', sa.Date(), nullable=True))
        batch_op.drop_column('dataInicio')
        batch_op.drop_column('dataFinal')


def downgrade():
    with op.batch_alter_table('turmas', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('dataFinal', sa.DATE(), nullable=True))
        batch_op.add_column(sa.Column('dataInicio', sa.DATE(), nullable=True))
        batch_op.drop_column('data_final')
        batch_op.drop_column('data_inicio')

    with op.batch_alter_table('secretaria', schema=None, recreate='always') as batch_op:
        batch_op.drop_constraint('uq_secretaria_email', type_='unique')

    with op.batch_alter_table('professor', schema=None, recreate='always') as batch_op:
        batch_op.drop_constraint('uq_professor_email', type_='unique')

    with op.batch_alter_table('materias', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('id_professor', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('id_turma', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint('fk_materia_professor', type_='foreignkey')
        batch_op.drop_constraint('fk_materia_turma', type_='foreignkey')
        batch_op.drop_column('turma_id')
        batch_op.drop_column('professor_id')