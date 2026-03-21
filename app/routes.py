
from wtforms import ValidationError
from app import app, db
from flask import Response, flash, make_response, render_template, send_file, url_for, request, redirect, abort, session
<<<<<<< Updated upstream
from app.models import Responsavel, User, TipoUsuario, Aluno, Turmas
=======
from app.models import Responsavel, Turmas, User, TipoUsuario, Aluno
>>>>>>> Stashed changes
from app.forms import AlunoForm, ProfessorForm, RespUserForm, ResponsavelForm, SecretariaForm, UserForm, LoginForm, TurmaForm

from sqlalchemy import desc

from openpyxl import Workbook
from io import BytesIO
import os

from flask_login import logout_user, login_user, current_user, login_required

from datetime import datetime, timezone

import csv


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        try:
            user = form.login()
            login_user(user, remember=True)
            session.permanent = True

            return redirect(url_for("home"))

        except ValidationError as erro:
            form.senha.errors.append(str(erro))

     
    
    return render_template('login.html', form=form)



@app.route('/home/', methods=['GET', 'POST'])
def home():
    # Dicionário que mapeia o nome da aba para o caminho do arquivo html

    return render_template('home.html')
    






# /////////////// USER ///////////////

@app.route('/registrar_user/', methods=['GET', 'POST'])
# @login_required
def registrar_user():
    form = UserForm()
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('home'))


    # print(form.tipo_usuario.data)
    # if form.tipo_usuario.data == 'RESPONSAVEL':

    #     if form.validate_on_submit():
    #         form.save()
    #         return redirect(url_for('registrar_user'))
    # if form.tipo_usuario.data == 'RESPONSAVEL':
    #     ...
    
    
    return render_template('register/registrar_user.html', form=form)






# /////////////// ALUNO ///////////////

@app.route('/registrar_aluno/', methods=['GET', 'POST'])
def registrar_aluno():
    turmas = Turmas.query.all()
    cpf = request.args.get('cpf') or request.form.get('cpf')
    formAluno = AlunoForm()

    if cpf:

        exists = Aluno.query.filter_by(cpf=cpf).first()

        if exists:
            msg = 'Aluno já cadastrado!'
            return render_template(
                'register/registrar_aluno.html',
                cpf=cpf,
                msg=msg,
                turmas=turmas
            )

        if request.method == "POST":
            print('entou no post')
            if formAluno.validate_on_submit():
                print('form valido')

                formAluno.save()
                FormRespUser = RespUserForm(formdata=None)

                return render_template(
                    'register/registrar_responsavel.html',
                    cpf=cpf,
                    FormRespUser=FormRespUser
                )


        return render_template(
            'register/registrar_aluno.html',
            cpf=cpf,
            formAluno=formAluno,
            origem='aluno',
            turmas=turmas
        )

    return render_template('register/registrar_aluno.html', turmas=turmas)


@app.route('/alunos/lista/')
def lista_alunos():
    turma_id = request.args.get('turma_id')

    if turma_id:
        alunos = Aluno.query.filter_by(turma_id=turma_id).all()
    else:
        alunos = Aluno.query.all()

    return render_template('partials/aluno_lista.html', alunos=alunos)


# /////////////// RESPONSAVEL ///////////////


@app.route('/registrar_responsavel/', methods=['GET', 'POST'])
def registrar_responsavel():

    FormRespUser = RespUserForm()

    cpf = request.form.get('cpf') or request.args.get('cpf')
    msg = None

    if cpf:
        aluno = Aluno.query.filter_by(cpf=cpf).first()


        if not aluno:
            msg = "Aluno não encontrado!"
    else:
        msg = "Aluno não encontrado!"


    if FormRespUser.validate_on_submit():
        print(FormRespUser.errors)
        responsavel = FormRespUser.save()

        aluno = Aluno.query.filter_by(cpf=cpf).first()
        responsavel.alunos.append(aluno)

        db.session.commit()

        return redirect(url_for('registrar_responsavel'))

    return render_template(
        'register/registrar_responsavel.html',
        FormRespUser=FormRespUser,
        cpf=cpf,
        msg=msg
    )





# /////////////// PROFESSOR ///////////////

@app.route('/registrar_professor/', methods=['GET', 'POST'])
# @login_required
def registrar_professor():
    form = ProfessorForm()

    print("VALID:", form.validate_on_submit())
    print("ERROS:", form.errors)
    print("FORM DATA:", request.form)

    if form.validate_on_submit():
        form.save()
        return redirect(url_for('registrar_professor'))
    
    return render_template('register/registrar_professor.html', form=form)




# /////////////// SECRETARIA ///////////////

@app.route('/registrar_secretaria/', methods=['GET', 'POST'])
# @login_required
def registrar_secretaria():
    formUser = UserForm()


    if formUser.validate_on_submit():
        formUser.save()
        formSec = SecretariaForm()
        return render_template('register/registrar_secretaria.html', formSec=formSec)
    
    formSec = SecretariaForm()

    if formSec.validate_on_submit():
        formSec.save()

        flash(f"Secretaria cadastrado no sistema ✅", "sucesso")
        return redirect(url_for('registrar_secretaria'))
    
    return render_template('register/registrar_secretaria.html', formUser=formUser)





@app.route('/documentos/', methods=['GET', 'POST'])
def documentos():
    if request.method == 'GET':
        return render_template('documentos.html')



@app.route('/gestao_academica/', methods=['GET', 'POST'])
def gestao_academica():
    if request.method == 'GET':
        return render_template('gestao_academica.html')



@app.route('/gestao_administrativa/', methods=['GET', 'POST'])
def gestao_administrativa():
    if request.method == 'GET':
        return render_template('gestao_administrativa.html')



@app.route('/alertas/', methods=['GET', 'POST'])
def alertas():
    if request.method == 'GET':
        return render_template('alertas.html')



@app.route('/calendario/', methods=['GET', 'POST'])
def calendario():
    if request.method == 'GET':
        return render_template('calendario.html')



@app.route('/turma/criar/', methods=['GET', 'POST'])
def criar_turma():
    turmaForm  = TurmaForm()

    if turmaForm.validate_on_submit():
        
        turma = turmaForm.save()
        if turma:
            msg='Turma cadastrada com sucesso!!'
            return render_template(
                'register/turmas.html',
                msg=msg,
            )

        return render_template(
            'register/turmas.html',
            turmaForm=turmaForm
        )

    return render_template('register/turmas.html', turmaForm=turmaForm)