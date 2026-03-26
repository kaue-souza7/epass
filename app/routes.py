
from wtforms import ValidationError
from app import app, db
from flask import Response, flash, make_response, render_template, send_file, url_for, request, redirect, abort, session
from app.models import Logradouro, Responsavel, User, TipoUsuario, Aluno, Turmas

from app.forms import AlunoForm, ProfessorForm, RespUserForm, ResponsavelForm, SecretariaForm, UserForm, LoginForm, TurmaForm

from sqlalchemy import desc

from openpyxl import Workbook
from io import BytesIO
import os

from flask_login import logout_user, login_user, current_user, login_required

from datetime import datetime, timezone

import csv


@app.route('/alunos/update_flash/')
def update_flash():
    return render_template('partials/flash.html')


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
    page = request.args.get('page', 1, type=int)

    if turma_id:
        alunos = Aluno.query.filter_by(turma_id=turma_id).paginate(page=page, per_page=8, error_out=False)
    else:
        alunos = Aluno.query.paginate(page=page, per_page=8, error_out=False)

    return render_template('partials/aluno_lista.html', alunos=alunos)


@app.route('/toggle_status/<int:id>', methods=['GET', 'POST'])
def toggle_status(id):
    aluno = Aluno.query.get_or_404(id)
    
    aluno.status = not aluno.status  # inverte True/False
    
    db.session.commit()
    
    return redirect(url_for('registrar_aluno')) 


@app.route('/alunos/update/<int:id>', methods=['GET', 'POST'])
def update_aluno(id):
    aluno = Aluno.query.get_or_404(id)
    form = AlunoForm(obj=aluno)  # 🔥 aqui já popula o form automaticamente

    # ✅ GET → popular form com logradouro
    if request.method == 'GET':
        if aluno.logradouro:
            form.cep.data = aluno.logradouro.cep
            form.rua.data = aluno.logradouro.rua
            form.numero.data = aluno.logradouro.numero
            form.bairro.data = aluno.logradouro.bairro
            form.cidade.data = aluno.logradouro.cidade
            form.estado.data = aluno.logradouro.estado

    print("VALIDOU?", form.validate_on_submit())
    print(form.errors)
    # ✅ POST → salvar alterações
    if form.validate_on_submit():
        form.populate_obj(aluno)

        if not aluno.logradouro:
            aluno.logradouro = Logradouro()

        aluno.logradouro.cep = form.cep.data
        aluno.logradouro.rua = form.rua.data
        aluno.logradouro.numero = form.numero.data
        aluno.logradouro.bairro = form.bairro.data
        aluno.logradouro.cidade = form.cidade.data
        aluno.logradouro.estado = form.estado.data

        db.session.commit()
        flash(f'Aluno atualizado com sucesso! ✅', 'sucesso')
        # o que eu posso fazer aqui jatestei tanto redirect quanto render template
        response = make_response('')
        response.headers['HX-Trigger'] = 'alunoAtualizado, mostrarFlash'
        return response


    return render_template('partials/aluno_update.html', form=form, aluno=aluno)




# /////////////// RESPONSAVEL ///////////////


@app.route('/registrar_responsavel/', methods=['GET', 'POST'])
def registrar_responsavel():
    turmas = Turmas.query.all()
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
        msg=msg,
        turmas=turmas
    )

@app.route('/responsavel/lista/')
def lista_responsavel():
    turma_id = request.args.get('turma_id')
    page = request.args.get('page', 1, type=int)

    if turma_id:
        responsaveis = (
            Responsavel.query
            .join(Responsavel.alunos)  # usa o relacionamento MANY-TO-MANY
            .filter(Aluno.turma_id == int(turma_id))
            .paginate(page=page, per_page=8, error_out=False)
        )
    else:
        responsaveis = Responsavel.query.paginate(page=page, per_page=8, error_out=False)

    return render_template('partials/responsavel_lista.html', responsaveis=responsaveis)




# /////////////// PROFESSOR ///////////////

@app.route('/registrar_professor/', methods=['GET', 'POST'])
# @login_required
def registrar_professor():
    formUser = UserForm(tipo_usuario='PROFESSOR')

    if formUser.validate_on_submit():
        formUser.save()
        form = ProfessorForm()
        return render_template('register/registrar_professor.html', form=form)

    # print("VALID:", form.validate_on_submit())
    # print("ERROS:", form.errors)
    # print("FORM DATA:", request.form)

    form = ProfessorForm()


    if form.validate_on_submit():
        form.save()
        flash(f"Professor cadastrado no sistema! ✅", "sucesso")

        return redirect(url_for('registrar_professor'))
    
    return render_template('register/registrar_professor.html', formUser=formUser)




# /////////////// SECRETARIA ///////////////

@app.route('/registrar_secretaria/', methods=['GET', 'POST'])
# @login_required
def registrar_secretaria():
    formUser = UserForm(tipo_usuario='SECRETARIA')


    if formUser.validate_on_submit():
        formUser.save()
        formSec = SecretariaForm()
        return render_template('register/registrar_secretaria.html', formSec=formSec)
    
    formSec = SecretariaForm()

    if formSec.validate_on_submit():
        formSec.save()

        flash(f"Secretaria cadastrado no sistema! ✅", "sucesso")
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