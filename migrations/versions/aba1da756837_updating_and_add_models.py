"""updating and add models

Revision ID: aba1da756837
Revises: 62f542485e31
Create Date: 2026-04-26 17:42:23.832234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aba1da756837'
down_revision = '62f542485e31'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    if not conn.dialect.has_table(conn, 'agendas'):
        op.create_table('agendas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('titulo', sa.String(length=100), nullable=False),
            sa.Column('descricao', sa.Text(), nullable=True),
            sa.Column('turma_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], name='fk_agendas_turma_id'),
            sa.PrimaryKeyConstraint('id', name='pk_agendas'),
            sa.UniqueConstraint('turma_id', name='uq_agendas_turma_id')
        )

    if not conn.dialect.has_table(conn, 'eventos'):
        op.create_table('eventos',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('titulo', sa.String(length=100), nullable=False),
            sa.Column('descricao', sa.Text(), nullable=True),
            sa.Column('data', sa.DateTime(), nullable=True),
            sa.Column('agenda_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['agenda_id'], ['agendas.id'], name='fk_eventos_agenda_id'),
            sa.PrimaryKeyConstraint('id', name='pk_eventos')
        )

    if not conn.dialect.has_table(conn, 'atividades'):
        op.create_table('atividades',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('titulo', sa.String(length=100), nullable=False),
            sa.Column('descricao', sa.Text(), nullable=True),
            sa.Column('data_entrega', sa.DateTime(), nullable=True),
            sa.Column('peso', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('materia_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['materia_id'], ['materias.id'], name='fk_atividades_materia_id'),
            sa.PrimaryKeyConstraint('id', name='pk_atividades')
        )

    if not conn.dialect.has_table(conn, 'aulas'):
        op.create_table('aulas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('titulo', sa.String(length=100), nullable=False),
            sa.Column('conteudo', sa.Text(), nullable=True),
            sa.Column('data', sa.DateTime(), nullable=True),
            sa.Column('materia_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['materia_id'], ['materias.id'], name='fk_aulas_materia_id'),
            sa.PrimaryKeyConstraint('id', name='pk_aulas')
        )

    if not conn.dialect.has_table(conn, 'frequencias'):
        op.create_table('frequencias',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('presente', sa.Boolean(), nullable=False),
            sa.Column('observacao', sa.Text(), nullable=True),
            sa.Column('aula_id', sa.Integer(), nullable=False),
            sa.Column('aluno_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['aluno_id'], ['aluno.id'], name='fk_frequencias_aluno_id'),
            sa.ForeignKeyConstraint(['aula_id'], ['aulas.id'], name='fk_frequencias_aula_id'),
            sa.PrimaryKeyConstraint('id', name='pk_frequencias'),
            sa.UniqueConstraint('aula_id', 'aluno_id', name='uq_frequencia_aula_aluno')
        )

    if not conn.dialect.has_table(conn, 'notas'):
        op.create_table('notas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('valor', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('observacao', sa.Text(), nullable=True),
            sa.Column('atividade_id', sa.Integer(), nullable=False),
            sa.Column('aluno_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['aluno_id'], ['aluno.id'], name='fk_notas_aluno_id'),
            sa.ForeignKeyConstraint(['atividade_id'], ['atividades.id'], name='fk_notas_atividade_id'),
            sa.PrimaryKeyConstraint('id', name='pk_notas'),
            sa.UniqueConstraint('atividade_id', 'aluno_id', name='uq_nota_atividade_aluno')
        )

    # Recria a tabela materias do zero para trocar id_professor/id_turma
    # por professor_id/turma_id com FKs nomeadas (obrigatório no SQLite)
    with op.batch_alter_table('materias', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('professor_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('turma_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_materia_turma', 'turmas', ['turma_id'], ['id'])
        batch_op.create_foreign_key('fk_materia_professor', 'professor', ['professor_id'], ['id'])
        batch_op.drop_column('id_professor')
        batch_op.drop_column('id_turma')

    with op.batch_alter_table('professor', schema=None, recreate='always') as batch_op:
        batch_op.create_unique_constraint('uq_professor_email', ['email'])

    with op.batch_alter_table('secretaria', schema=None, recreate='always') as batch_op:
        batch_op.create_unique_constraint('uq_secretaria_email', ['email'])

    with op.batch_alter_table('turmas', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('data_inicio', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('data_final', sa.Date(), nullable=True))
        batch_op.drop_column('dataFinal')
        batch_op.drop_column('dataInicio')

    with op.batch_alter_table('user', schema=None, recreate='always') as batch_op:
        batch_op.create_unique_constraint('uq_user_email', ['email'])


def downgrade():


    with op.batch_alter_table('turmas', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('dataInicio', sa.DATE(), nullable=True))
        batch_op.add_column(sa.Column('dataFinal', sa.DATE(), nullable=True))
        batch_op.drop_column('data_final')
        batch_op.drop_column('data_inicio')

    with op.batch_alter_table('secretaria', schema=None, recreate='always') as batch_op:
        batch_op.drop_constraint('uq_secretaria_email', type_='unique')

    with op.batch_alter_table('professor', schema=None, recreate='always') as batch_op:
        batch_op.drop_constraint('uq_professor_email', type_='unique')

    with op.batch_alter_table('materias', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('id_professor', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('id_turma', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_materia_professor', type_='foreignkey')
        batch_op.drop_constraint('fk_materia_turma', type_='foreignkey')
        batch_op.drop_column('professor_id')
        batch_op.drop_column('turma_id')

    op.drop_table('notas')
    op.drop_table('frequencias')
    op.drop_table('aulas')
    op.drop_table('atividades')
    op.drop_table('eventos')
    op.drop_table('agendas')