from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, PasswordField, SelectField, DateField, DecimalField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

import os
from werkzeug.utils import secure_filename

from app import db, bcrypt, app
from app.models import Aluno, Professor, User, TipoUsuario



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





class AlunoForm(FlaskForm):

    nome = StringField(
        "Nome",
        validators=[DataRequired(), Length(max=100)]
    )
    sobrenome = StringField(
        "Sobrenome",
        validators=[DataRequired(), Length(max=100)]
    )

    cpf = StringField(
        "CPF",
        validators=[DataRequired(), Length(min=11, max=14)]
    )

    endereco = StringField(
        "Endereço",
        validators=[DataRequired(), Length(max=255)]
    )

    nascimento = DateField(
        "Data de Nascimento",
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )

    status = BooleanField(
        "Ativo"
    )

    btnSubmit = SubmitField("Salvar")
    def save(self):

        aluno = Aluno(
            nome= self.nome.data,
            sobrenome= self.sobrenome.data,
            cpf=self.cpf.data,
            endereco=self.endereco.data,
            nascimento=self.nascimento.data,
            status=self.status.data,

        )

        db.session.add(aluno)
        db.session.commit()
        return aluno
    


class ProfessorForm(FlaskForm):

    cpf = StringField(
        "CPF",
        validators=[DataRequired(), Length(min=11, max=14)]
    )

    telefone = StringField(
        "Telefone",
        validators=[DataRequired(), Length(max=20)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Length(max=150)]
    )

    endereco = StringField(
        "Endereço",
        validators=[DataRequired(), Length(max=255)]
    )

    formacao = StringField(
        "Formação",
        validators=[DataRequired(), Length(max=150)]
    )

    turno = SelectField(
        "Turno",
        choices=[
            ("manha", "Manhã"),
            ("tarde", "Tarde"),
            ("noite", "Noite")
        ],
        validators=[DataRequired()]
    )

    nascimento = DateField(
        "Data de Nascimento",
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )

    status = BooleanField("Ativo")

    btnSubmit = SubmitField("Salvar")

    def save(self, user_id):

        professor = Professor(
            cpf=self.cpf.data,
            telefone=self.telefone.data,
            email=self.email.data,
            endereco=self.endereco.data,
            formacao=self.formacao.data,
            turno=self.turno.data,
            nascimento=self.nascimento.data,
            status=self.status.data,
            user_id=user_id
        )

        db.session.add(professor)
        db.session.commit()
        return professor