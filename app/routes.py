
from wtforms import ValidationError
from app import app, db
from flask import Response, make_response, render_template, send_file, url_for, request, redirect, abort, session
from app.models import Responsavel, User, TipoUsuario, Aluno
from app.forms import AlunoForm, ProfessorForm, RespUserForm, ResponsavelForm, SecretariaForm, UserForm, LoginForm

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
    print(form.tipo_usuario.data)
    if form.tipo_usuario.data == 'RESPONSAVEL':

        if form.validate_on_submit():
            # form.save()
            return redirect(url_for('registrar_user'))
    if form.tipo_usuario.data == 'RESPONSAVEL':
        ...
    
    
    return render_template('register/registrar_user.html', form=form)






# /////////////// ALUNO ///////////////

@app.route('/registrar_aluno/', methods=['GET', 'POST'])
def registrar_aluno():

    cpf = request.args.get('cpf') or request.form.get('cpf')
    formAluno = AlunoForm()

    if cpf:

        exists = Aluno.query.filter_by(cpf=cpf).first()

        if exists:
            msg = 'Aluno já cadastrado!'
            return render_template(
                'register/registrar_aluno.html',
                cpf=cpf,
                msg=msg
            )

        if request.method == "POST":
            print('entou no post')
            if formAluno.validate_on_submit():
                print('form valido')

                formAluno.save()

                response = make_response("")
                response.headers["HX-Redirect"] = url_for(
                    "registrar_responsavel",
                    cpf=cpf
                )

                return response

        return render_template(
            'register/registrar_aluno.html',
            cpf=cpf,
            formAluno=formAluno,
            origem='aluno'
        )

    return render_template('register/registrar_aluno.html')






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



    if form.validate_on_submit():
        form.save()
        return redirect(url_for('registrar_professor'))
    
    return render_template('register/registrar_professor.html', form=form)





# /////////////// SECRETARIA ///////////////

@app.route('/registrar_secretaria/', methods=['GET', 'POST'])
# @login_required
def registrar_secretaria():
    form = SecretariaForm()



    if form.validate_on_submit():
        form.save()
        return redirect(url_for('registrar_secretaria'))
    
    return render_template('register/registrar_secretaria.html', form=form)






