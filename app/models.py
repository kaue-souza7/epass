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



