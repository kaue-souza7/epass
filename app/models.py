import uuid
from app import db
from datetime import datetime, timezone
from flask_login import UserMixin

import enum

class TipoUsuario(enum.Enum):
    RESPONSAVEL = "responsavel"
    SECRETARIA = "secretaria"
    ADMIN = "admin"
    PROFESSOR = "professor"

class TipoDocumento(enum.Enum):
    CARTEIRA_ESCOLAR = "2 Via Carteira Escolar"
    ATESTADO_MATRICULA = "Atestado de Matricula"
    BOLETIM = "Boletim"
    DCLR_TRANSF = "Declaração de Transferência"
    HIST_ESCOLAR = "Histórico Escolar"
    GRADE_ESCOLAR = "Grade Escolar"



class StatusDocumento(enum.Enum):
    PENDENTE = "pendente"
    EM_ANALISE = "em_analise"
    PRONTO = "pronto"
    ENTREGUE = "entregue"


class TipoSanguineo(enum.Enum):
    A_POSITIVO = "A+"
    A_NEGATIVO = "A-"
    B_POSITIVO = "B+"
    B_NEGATIVO = "B-"
    AB_POSITIVO = "AB+"
    AB_NEGATIVO = "AB-"
    O_POSITIVO = "O+"
    O_NEGATIVO = "O-"

class Logradouro(db.Model):
    __tablename__ = 'logradouros'

    id = db.Column(db.Integer, primary_key=True)
    rua = db.Column(db.String(150))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(10))



responsavel_aluno = db.Table(
    "responsavel_aluno",

    db.Column(
        "responsavel_id",
        db.Integer,
        db.ForeignKey("responsavel.id"),
        primary_key=True
    ),

    db.Column(
        "aluno_id",
        db.Integer,
        db.ForeignKey("aluno.id"),
        primary_key=True
    )
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)
    tipo_usuario = db.Column(db.Enum(TipoUsuario), nullable=False)


    professor = db.relationship("Professor", backref="user", uselist=False)
    secretaria = db.relationship("Secretaria", backref="user", uselist=False)
    responsavel = db.relationship("Responsavel", backref="user", uselist=False)



class Aluno(db.Model):
    __tablename__ = 'aluno'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    nascimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    matricula = db.Column(db.String(20), nullable=True)
    data_matricula = db.Column(db.Date, nullable=True)
    tipo_sanguineo = db.Column(db.Enum(TipoSanguineo), nullable=True)

    responsaveis = db.relationship(
        'Responsavel',
        secondary=responsavel_aluno,
        back_populates='alunos'
    )

    turma_id = db.Column(
        db.Integer,
        db.ForeignKey('turmas.id', name='fk_aluno_turma'),
        nullable=True
    )

    logradouro_id = db.Column(
        db.Integer,
        db.ForeignKey('logradouros.id', name='fk_aluno_logradouro'),
        nullable=True
    )
    logradouro = db.relationship('Logradouro')

    carteira = db.relationship(
        'Carteira',
        uselist=False,
        back_populates='aluno'
    )

    frequencias = db.relationship(
        'Frequencia',
        back_populates='aluno',
        lazy=True,
        cascade='all, delete-orphan'
    )

    notas = db.relationship(
        'Nota',
        back_populates='aluno',
        lazy=True,
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.UniqueConstraint('matricula', name='uq_aluno_matricula'),
    )


    def __str__(self):
        return self.nome

class Documento(db.Model):
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)

    tipo_documento = db.Column(db.Enum(TipoDocumento), nullable=False)

    data_pedido = db.Column(db.DateTime, default=db.func.current_timestamp())
    data_emissao = db.Column(db.DateTime, nullable=True)
    observacao = db.Column(db.Text)
    status = db.Column(db.Enum(StatusDocumento), default=StatusDocumento.PENDENTE)

    # RELACIONAMENTOS
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=True)

    # ARQUIVO
    path = db.Column(db.String(255), nullable=True)

    # RELATIONSHIPS
    aluno = db.relationship('Aluno', backref='documentos')
    turma = db.relationship('Turmas', backref='documentos')
    professor = db.relationship('Professor', backref='documentos')






class Carteira(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Float, default=0.0)
    aluno_id = db.Column(
        db.Integer,
        db.ForeignKey('aluno.id'),
        unique=True,
        nullable=False
    )

    aluno = db.relationship(
        'Aluno',
        back_populates='carteira'
    )


class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tipo = db.Column(db.String(20))  # 'entrada', 'saida'
    valor = db.Column(db.Float)
    descricao = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=db.func.current_timestamp())

    carteira_id = db.Column(
        db.Integer,
        db.ForeignKey('carteira.id'),
        nullable=False
    )
    carteira = db.relationship('Carteira', backref='transacoes')    



class PagamentoPendente(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsavel.id'), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente | confirmado
    qr_code = db.Column(db.String(200))
    copia_cola = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime, default=db.func.current_timestamp())

    responsavel = db.relationship('Responsavel', backref='pagamentos_pendentes')
    aluno = db.relationship('Aluno', backref='pagamentos_pendentes')


class Professor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    formacao = db.Column(db.String(150), nullable=False)
    turno = db.Column(db.String(20), nullable=False)  # manhã, tarde, noite
    nascimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    logradouro_id = db.Column(db.Integer, db.ForeignKey('logradouros.id', name='fk_professor_logradouro'), nullable=True)
    logradouro = db.relationship('Logradouro')
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)

    materias = db.relationship('Materia', backref='professor', lazy=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", name="uq_professor_user_id"),
    )



class Secretaria(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    endereco = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(120), nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )



class Responsavel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), nullable=False)
    nascimento = db.Column(db.Date, nullable=False)


    logradouro_id = db.Column(db.Integer, db.ForeignKey('logradouros.id', name='fk_responsavel_logradouro'), nullable=True)
    logradouro = db.relationship('Logradouro')

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    alunos = db.relationship(
        "Aluno",
        secondary=responsavel_aluno,
        back_populates="responsaveis"
    )

    def __str__(self):
        return self.user.nome




class Turmas(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ano = db.Column(db.Integer, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_final = db.Column(db.Date)
    periodo = db.Column(db.String(50))

    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    materias = db.relationship('Materia', backref='turma', lazy=True)
    agenda = db.relationship('Agenda', backref='turma', uselist=False, cascade='all, delete-orphan')



class Materia(db.Model):
    __tablename__ = 'materias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=True)
    descricao = db.Column(db.Text)

    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id', name='fk_materia_professor'), nullable=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True)

    aulas = db.relationship(
        'Aula',
        back_populates='materia',
        lazy=True,
        cascade='all, delete-orphan'
    )

    atividades = db.relationship(
        'Atividade',
        back_populates='materia',
        lazy=True,
        cascade='all, delete-orphan'
    )


class TipoAvisoEnum(enum.Enum):
    GERAL = "geral"
    COMPORTAMENTO = "comportamento"
    SAUDE = "saude"
    ADMINISTRATIVO = "administrativo"


class NivelPrioridadeAviso(enum.Enum):
    BAIXA = 'baixa'
    MEDIA = 'media'
    ALTA = 'alta'




class Aviso(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(150))
    mensagem = db.Column(db.Text)
    tipo = db.Column(db.Enum(TipoAvisoEnum), nullable=False)

    remetente_id = db.Column(db.Integer)
    remetente_tipo = db.Column(db.String(20))

    prioridade = db.Column(
        db.Enum(
            NivelPrioridadeAviso,
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=False
    )

    data_criacao = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    data_envio = db.Column(db.DateTime)

    enviado = db.Column(db.Boolean, default=False)




class AvisoDestinatario(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    aviso_id = db.Column(db.Integer, db.ForeignKey('aviso.id'))

    destinatario_id = db.Column(db.Integer)
    destinatario_tipo = db.Column(db.String(20))  # 'professor' ou 'responsavel'

    lido = db.Column(db.Boolean, default=False)

    aviso = db.relationship('Aviso', backref='destinatarios')






class Aula(db.Model):
    __tablename__ = 'aulas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.Text)
    data = db.Column(db.DateTime, nullable=True)

    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)

    materia = db.relationship('Materia', back_populates='aulas')
    frequencias = db.relationship(
        'Frequencia',
        back_populates='aula',
        lazy=True,
        cascade='all, delete-orphan'
    )


    
class Frequencia(db.Model):
    __tablename__ = 'frequencias'

    id = db.Column(db.Integer, primary_key=True)
    presente = db.Column(db.Boolean, nullable=False, default=False)
    observacao = db.Column(db.Text)

    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)

    aula = db.relationship('Aula', back_populates='frequencias')
    aluno = db.relationship('Aluno', back_populates='frequencias')

    __table_args__ = (
        db.UniqueConstraint('aula_id', 'aluno_id', name='uq_frequencia_aula_aluno'),
    )


class Atividade(db.Model):
    __tablename__ = 'atividades'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_entrega = db.Column(db.DateTime, nullable=True)
    peso = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)

    materia = db.relationship('Materia', back_populates='atividades')
    notas = db.relationship(
        'Nota',
        back_populates='atividade',
        lazy=True,
        cascade='all, delete-orphan'
    )




class Nota(db.Model):
    __tablename__ = 'notas'

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    observacao = db.Column(db.Text)

    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)

    atividade = db.relationship('Atividade', back_populates='notas')
    aluno = db.relationship('Aluno', back_populates='notas')

    __table_args__ = (
        db.UniqueConstraint('atividade_id', 'aluno_id', name='uq_nota_atividade_aluno'),
    )

class Agenda(db.Model):
    __tablename__ = 'agendas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)

    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False, unique=True)
    eventos = db.relationship('Evento', backref='agenda', lazy=True, cascade='all, delete-orphan')



class Evento(db.Model):
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data = db.Column(db.DateTime, nullable=True)

    agenda_id = db.Column(db.Integer, db.ForeignKey('agendas.id'), nullable=False)




