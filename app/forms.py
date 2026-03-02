from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, DateField, DecimalField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

import os
from werkzeug.utils import secure_filename

from app import db, bcrypt, app
from app.models import User, TipoUsuario



class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confirmação Senha', validators=[DataRequired(), EqualTo('senha')])
    tipo_usuario = SelectField('Tipo de usuário',
                               choices=[('RESPONSAVEL', 'Responsavel'),('SECRETARIA', 'Secretaria'),('ADMIN', 'Administrador')], 
                               validators=[DataRequired()]) 

    btnSubmit = SubmitField('Cadastrar')


    def validade_email(self, email):
        if User.query.filter(email=email.data).first():
            return ValidationError('Usuário ja cadastrado!')
    

    def save(self):
        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))

        user = User(
            nome= self.nome.data,
            sobrenome= self.sobrenome.data,
            email=self.email.data,
            senha=senha,
            tipo_usuario=TipoUsuario[self.tipo_usuario.data],

        )

        db.session.add(user)
        db.session.commit()
        return user
    



class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Sign-in')

    def login(self):
        # Recuperar usuario do e-mail
        user = User.query.filter_by(email=self.email.data).first()

        # Verificar se a senha é válida
        if user:
            if bcrypt.check_password_hash(user.senha, self.senha.data.encode('utf-8')):
                # Retorna o Usuário
                return user
            else: raise Exception('Senha ou E-mail incorreto(s).')


        else: raise Exception('Usuário não encontrado.')