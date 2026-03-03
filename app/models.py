from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

import enum

class TipoUsuario(enum.Enum):
    RESPONSAVEL = "responsavel"
    SECRETARIA = "secretaria"
    ADMIN = "admin"



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)
    tipo_usuario = db.Column(db.Enum(TipoUsuario), nullable=False)


    professor = db.relationship("Professor", backref="user", uselist=False)



class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    nascimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


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


    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))




