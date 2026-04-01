from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectMultipleField, StringField, SubmitField, PasswordField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
import wtforms
import os
from werkzeug.utils import secure_filename

from app import db, bcrypt, app
from app.models import Aluno, Documento, Logradouro, Professor, Responsavel, Secretaria, StatusDocumento, TipoDocumento, TipoSanguineo, Turmas, User, TipoUsuario


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
    nascimento = DateField( "Data de Nascimento", format='%Y-%m-%d', validators=[DataRequired()])
    status = BooleanField("Ativo")

    matricula = StringField("Matrícula", validators=[Optional(), Length(max=20)])
    data_matricula = DateField("Data da Matrícula", format='%Y-%m-%d', validators=[Optional()])
    tipo_sanguineo = SelectField(
        "Tipo Sanguíneo",
        choices=[(ts.name, ts.value) for ts in TipoSanguineo],
        validators=[Optional()]
    )


    turma_id = SelectField("Turma", coerce=int)

    btnSubmit = SubmitField("Salvar")

    cep = StringField("CEP", validators=[DataRequired(), Length(min=8, max=9)])
    rua = StringField("Rua", validators=[DataRequired(), Length(max=150)])
    numero = StringField("Número", validators=[DataRequired(), Length(max=10)])
    bairro = StringField("Bairro", validators=[DataRequired(), Length(max=100)])
    cidade = StringField("Cidade", validators=[DataRequired(), Length(max=100)])
    estado = StringField("Estado", validators=[DataRequired(), Length(max=2)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        turmas = Turmas.query.all()

        self.turma_id.choices = [(0, "Sem turma")] + [
            (turma.id, turma.nome) for turma in turmas
        ]



    def save(self):

        turma_id = self.turma_id.data if self.turma_id.data != 0 else None

        logradouro = Logradouro(
            cep=self.cep.data,
            rua=self.rua.data,
            numero=self.numero.data,
            bairro=self.bairro.data,
            cidade=self.cidade.data,
            estado=self.estado.data
        )

        db.session.add(logradouro)
        db.session.flush()  

        aluno = Aluno(
            nome= self.nome.data,
            sobrenome= self.sobrenome.data,
            cpf=self.cpf.data,
            nascimento=self.nascimento.data,
            status=self.status.data,
            turma_id=turma_id,
            matricula=self.matricula.data,
            data_matricula=self.data_matricula.data,
            tipo_sanguineo=TipoSanguineo[self.tipo_sanguineo.data] if self.tipo_sanguineo.data else None,
            logradouro=logradouro,
        )

        db.session.add(aluno)
        db.session.commit()
        return aluno
    


class ProfessorForm(FlaskForm):


    cpf = StringField("CPF",validators=[DataRequired(), Length(min=11, max=14)])
    telefone = StringField("Telefone",validators=[DataRequired(), Length(max=20)])
    email = StringField("Email",validators=[DataRequired(), Length(max=150)])
    formacao = StringField("Formação",validators=[DataRequired(), Length(max=150)])

    turno = SelectField(
        "Turno",
        choices=[
            ("manha", "Manhã"),
            ("tarde", "Tarde"),
            ("noite", "Noite")
        ],
        validators=[DataRequired()]
    )


    cep = StringField("CEP", validators=[DataRequired(), Length(min=8, max=9)])
    rua = StringField("Rua", validators=[DataRequired(), Length(max=150)])
    numero = StringField("Número", validators=[DataRequired(), Length(max=10)])
    bairro = StringField("Bairro", validators=[DataRequired(), Length(max=100)])
    cidade = StringField("Cidade", validators=[DataRequired(), Length(max=100)])
    estado = StringField("Estado", validators=[DataRequired(), Length(max=2)])




    nascimento = DateField("Data de Nascimento",format='%Y-%m-%d',validators=[DataRequired()])
    user_id = SelectField("Usuário Professor",coerce=int,validators=[DataRequired()])
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

        logradouro = Logradouro(
            cep=self.cep.data,
            rua=self.rua.data,
            numero=self.numero.data,
            bairro=self.bairro.data,
            cidade=self.cidade.data,
            estado=self.estado.data
        )

        db.session.add(logradouro)
        db.session.flush()  

        professor = Professor(
            cpf=self.cpf.data,
            telefone=self.telefone.data,
            email=self.email.data,
            formacao=self.formacao.data,
            turno=self.turno.data,
            nascimento=self.nascimento.data,
            status=self.status.data,
            user_id=self.user_id.data,
            logradouro=logradouro
        )

        db.session.add(professor)
        db.session.commit()
        return professor

    



class SecretariaForm(FlaskForm):

    telefone = StringField("Telefone", validators=[DataRequired(), Length(max=20)])
    email = StringField("Email",validators=[DataRequired(),Email(),Length(max=120)])
    endereco = StringField("Endereço",validators=[DataRequired(),Length(max=200)])
    website = StringField("Website",validators=[DataRequired(),Length(max=120)])
    
    user_id = SelectField("Usuário",coerce=int,validators=[DataRequired()])
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
    nascimento = DateField("Data de Nascimento", format="%Y-%m-%d", validators=[DataRequired()])

    btnSubmit = SubmitField("Salvar")


    cep = StringField("CEP", validators=[DataRequired(), Length(min=8, max=9)])
    rua = StringField("Rua", validators=[DataRequired(), Length(max=150)])
    numero = StringField("Número", validators=[DataRequired(), Length(max=10)])
    bairro = StringField("Bairro", validators=[DataRequired(), Length(max=100)])
    cidade = StringField("Cidade", validators=[DataRequired(), Length(max=100)])
    estado = StringField("Estado", validators=[DataRequired(), Length(max=2)])


    def __init__(self, *args, **kwargs):   
        super().__init__(*args, **kwargs)




    def save(self):

        logradouro = Logradouro(
            cep=self.cep.data,
            rua=self.rua.data,
            numero=self.numero.data,
            bairro=self.bairro.data,
            cidade=self.cidade.data,
            estado=self.estado.data
        )

        db.session.add(logradouro)
        db.session.flush()  

        responsavel = Responsavel(
            telefone=self.telefone.data,
            nascimento=self.nascimento.data,
            logradouro=logradouro,

        )

        



        db.session.add(responsavel)
        db.session.commit()
        return responsavel
    


class RespUserForm(FlaskForm):
    telefone = StringField("Telefone", validators=[DataRequired(), Length(max=20)])
    nascimento = DateField("Data de Nascimento", format="%Y-%m-%d", validators=[DataRequired()])


    # alunos = QuerySelectMultipleFieldwithCheckboxes('Alunos')
    cep = StringField("CEP", validators=[DataRequired(), Length(min=8, max=9)])
    rua = StringField("Rua", validators=[DataRequired(), Length(max=150)])
    numero = StringField("Número", validators=[DataRequired(), Length(max=10)])
    bairro = StringField("Bairro", validators=[DataRequired(), Length(max=100)])
    cidade = StringField("Cidade", validators=[DataRequired(), Length(max=100)])
    estado = StringField("Estado", validators=[DataRequired(), Length(max=2)])


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

        logradouro = Logradouro(
            cep=self.cep.data,
            rua=self.rua.data,
            numero=self.numero.data,
            bairro=self.bairro.data,
            cidade=self.cidade.data,
            estado=self.estado.data
        )

        db.session.add(logradouro)
        db.session.flush()  
        

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
            nascimento=self.nascimento.data,
            user_id=user.id,
            logradouro=logradouro,


        )

        db.session.add(responsavel)
        db.session.commit()
        return responsavel





class TurmaForm(FlaskForm):

    nome = StringField("Nome", validators=[DataRequired(), Length(max=100)])
    descricao = StringField("Descrição", validators=[Length(max=255)])
    ano = IntegerField("Ano", validators=[DataRequired()])
    dataInicio = DateField("Data de Início", format='%Y-%m-%d', validators=[DataRequired()])
    dataFinal = DateField("Data Final", format='%Y-%m-%d')
    periodo = StringField("Período", validators=[DataRequired(), Length(max=50)])

    btnSubmit = SubmitField("Salvar")

    def save(self):

        turma = Turmas(
            nome=self.nome.data,
            descricao=self.descricao.data,
            ano=self.ano.data,
            dataInicio=self.dataInicio.data,
            dataFinal=self.dataFinal.data,
            periodo=self.periodo.data
        )

        db.session.add(turma)
        db.session.commit()
        return turma
    








class DocumentoForm(FlaskForm):
    tipo_documento = SelectField(
        "Tipo de Documento",
        choices=[(tipo.name, tipo.value) for tipo in TipoDocumento],
        validators=[DataRequired()]
    )

    observacao = TextAreaField("Observação", validators=[Optional()])

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario  # quem está logado

    # 🔒 VALIDAÇÃO PRINCIPAL
    def validate_tipo_documento(self, field):
        tipo = TipoDocumento[field.data]

        # Se for professor, só pode pedir Declaração de Transferência
        if self.usuario.tipo == "professor":
            if tipo != TipoDocumento.DCLR_TRANSF:
                raise ValidationError(
                    "Professor só pode solicitar Declaração de Transferência."
                )

    # 💾 MÉTODO SAVE
    def save(self):
        tipo = TipoDocumento[self.tipo_documento.data]

        documento = Documento(
            tipo_documento=tipo,
            observacao=self.observacao.data,
            status=StatusDocumento.PENDENTE
        )

        # 👇 REGRA: OU ALUNO OU PROFESSOR
        if self.usuario.tipo == "aluno":
            documento.aluno_id = self.usuario.id
            documento.professor_id = None

        elif self.usuario.tipo == "professor":
            documento.professor_id = self.usuario.id
            documento.aluno_id = None

        else:
            raise Exception("Tipo de usuário inválido")

        # Outros campos automáticos
        documento.data_pedido = db.func.current_timestamp()

        db.session.add(documento)
        db.session.commit()

        return documento