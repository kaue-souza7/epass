from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectMultipleField, StringField, SubmitField, PasswordField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
import wtforms
import os
from werkzeug.utils import secure_filename

from app import db, bcrypt, app
from app.models import Aluno, Professor, Responsavel, Secretaria, User, TipoUsuario


class QuerySelectMultipleFieldwithCheckboxes(QuerySelectMultipleField):
    widget = wtforms.widgets.ListWidget(prefix_label=False)
    option_widget = wtforms.widgets.CheckboxInput()

class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confirmação Senha', validators=[DataRequired(), EqualTo('senha')])
    tipo_usuario = SelectField('Tipo de usuário',
                               choices=[('RESPONSAVEL', 'Responsavel'),('SECRETARIA', 'Secretaria'),('ADMIN', 'Administrador'),("PROFESSOR", "Professor")], 
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
    btnSubmit = SubmitField('Login')

    def login(self):
        # Recuperar usuario do e-mail
        user = User.query.filter_by(email=self.email.data).first()

        # Verificar se a senha é válida
        if user:
            if bcrypt.check_password_hash(user.senha, self.senha.data.encode('utf-8')):
                # Retorna o Usuário
                return user
            else: raise ValidationError('Usuário ou senha incorretos.')


        else: raise ValidationError('Usuário ou senha incorretos.')





class AlunoForm(FlaskForm):

    nome = StringField( "Nome", validators=[DataRequired(), Length(max=100)])
    sobrenome = StringField( "Sobrenome", validators=[DataRequired(), Length(max=100)])
    cpf = StringField( "CPF", validators=[DataRequired(), Length(min=11, max=14)])
    endereco = StringField( "Endereço", validators=[DataRequired(), Length(max=255)])
    nascimento = DateField( "Data de Nascimento", format='%Y-%m-%d', validators=[DataRequired()])
    status = BooleanField("Ativo")

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

    user_id = SelectField(
        "Usuário Professor",
        coerce=int,
        validators=[DataRequired()]
    )

    status = BooleanField("Ativo")

    btnSubmit = SubmitField("Salvar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Import aqui dentro para evitar circular import
        from app.models import User


        usuarios_disponiveis = User.query.filter_by(tipo_usuario="PROFESSOR").filter(
            User.professor == None
        ).all()

        self.user_id.choices = [
            (u.id, u.nome) for u in usuarios_disponiveis
        ]

    def save(self):

        professor = Professor(
            cpf=self.cpf.data,
            telefone=self.telefone.data,
            email=self.email.data,
            endereco=self.endereco.data,
            formacao=self.formacao.data,
            turno=self.turno.data,
            nascimento=self.nascimento.data,
            status=self.status.data,
            user_id=self.user_id.data,
        )

        db.session.add(professor)
        db.session.commit()
        return professor

    



class SecretariaForm(FlaskForm):

    telefone = StringField(
        "Telefone",
        validators=[
            DataRequired(),
            Length(max=20)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )

    endereco = StringField(
        "Endereço",
        validators=[
            DataRequired(),
            Length(max=200)
        ]
    )

    website = StringField(
        "Website",
        validators=[
            DataRequired(),
            Length(max=120)
        ]
    )

    user_id = SelectField(
        "Usuário",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Salvar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apenas usuários do tipo secretaria que ainda não têm vínculo
        self.user_id.choices = [
            (u.id, u.nome)
            for u in User.query.filter_by(tipo_usuario="SECRETARIA").all()
            if not u.secretaria
        ]

    def save(self):
        secretaria = Secretaria(
            telefone=self.telefone.data,
            email=self.email.data,
            endereco=self.endereco.data,
            website=self.website.data,
            user_id=self.user_id.data
        )

        db.session.add(secretaria)
        db.session.commit()
        return secretaria
    



class ResponsavelForm(FlaskForm):

    telefone = StringField("Telefone", validators=[DataRequired(), Length(max=20)])
    endereco = StringField("Endereço", validators=[DataRequired(), Length(max=200)])
    nascimento = DateField("Data de Nascimento", format="%Y-%m-%d", validators=[DataRequired()])

    btnSubmit = SubmitField("Salvar")
    user_id = SelectField("Usuário", coerce=int, validators=[DataRequired()])

    # alunos = QuerySelectMultipleFieldwithCheckboxes('Alunos')


    def __init__(self, *args, **kwargs):   
        super().__init__(*args, **kwargs)

        # Apenas usuários do tipo responsavel que ainda não têm vínculo
        self.user_id.choices = [
            (u.id, u.nome)
            for u in User.query.filter_by(tipo_usuario="RESPONSAVEL").all()
            if not u.responsavel
        ]


    def save(self):

        responsavel = Responsavel(
            telefone=self.telefone.data,
            endereco=self.endereco.data,
            nascimento=self.nascimento.data,
            user_id=self.user_id.data,
        )

        



        db.session.add(responsavel)
        db.session.commit()
        return responsavel
    


class RespUserForm(FlaskForm):
    telefone = StringField("Telefone", validators=[DataRequired(), Length(max=20)])
    endereco = StringField("Endereço", validators=[DataRequired(), Length(max=200)])
    nascimento = DateField("Data de Nascimento", format="%Y-%m-%d", validators=[DataRequired()])


    # alunos = QuerySelectMultipleFieldwithCheckboxes('Alunos')


    def __init__(self, *args, **kwargs):   
        super().__init__(*args, **kwargs)



    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confirmação Senha', validators=[DataRequired(), EqualTo('senha')])
    tipo_usuario = SelectField('Tipo de usuário',
                               choices=[('RESPONSAVEL', 'Responsavel'),('SECRETARIA', 'Secretaria'),('ADMIN', 'Administrador'),("PROFESSOR", "Professor")], 
                               validators=[DataRequired()]) 
    




    btnSubmit = SubmitField('Cadastrar')


    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            return ValidationError('Usuário ja cadastrado!')

    def save(self):
        

        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))  

        user = User(
            nome=self.nome.data,
            sobrenome=self.sobrenome.data,
            email=self.email.data,
            senha=senha,
            tipo_usuario=TipoUsuario[self.tipo_usuario.data],
        )

        db.session.add(user)
        db.session.flush()  # gera o id sem dar commit

        responsavel = Responsavel(
            telefone=self.telefone.data,
            endereco=self.endereco.data,
            nascimento=self.nascimento.data,
            user_id=user.id

        )

        db.session.add(responsavel)
        db.session.commit()
        return responsavel
