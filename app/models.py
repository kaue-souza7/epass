from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

import enum

class TipoUsuario(enum.Enum):
    RESPONSAVEL = "responsavel"
    SECRETARIA = "secretaria"
    ADMIN = "admin"
    PROFESSOR = "professor"


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
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    nascimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    responsaveis = db.relationship(
        "Responsavel",
        secondary=responsavel_aluno,
        back_populates="alunos"
    )

    def __str__(self):
        return self.nome
        

class Professor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    formacao = db.Column(db.String(150), nullable=False)
    turno = db.Column(db.String(20), nullable=False)  # manhã, tarde, noite
    nascimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", name="uq_professor_user_id"),
    )



class Secretaria(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
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
    endereco = db.Column(db.String(200), nullable=False)
    nascimento = db.Column(db.Date, nullable=False)



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



