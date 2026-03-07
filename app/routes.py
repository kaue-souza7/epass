
from app import app, db
from flask import Response, render_template, send_file, url_for, request, redirect, abort, session
from app.models import Responsavel, User, TipoUsuario, Aluno
from app.forms import AlunoForm, ProfessorForm, RespUserForm, ResponsavelForm, SecretariaForm, UserForm, LoginForm

from sqlalchemy import desc

from openpyxl import Workbook
from io import BytesIO
import os

from flask_login import logout_user, login_user, current_user, login_required

from datetime import datetime, timezone

import csv



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



@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
        session.permanent = True
        return redirect(url_for('home'))
    
    return render_template('login.html', form=form)



@app.route('/home/', methods=['GET', 'POST'])
# @login_required
def home():
 
    
    return render_template('home.html')




@app.route('/registrar_aluno/', methods=['GET', 'POST'])
# @login_required
def registrar_aluno():
    # form.alunos.query = Aluno.query.all()

    cpf = request.args.get('cpf') or None
    print(cpf)
    formAluno = AlunoForm()



    if cpf is not None:
        exists = Aluno.query.filter_by(cpf=cpf).first()
        print(exists)
        if exists:
            msg = 'Aluno ja cadastrado!'
            return render_template('register/registrar_aluno.html', cpf=cpf, msg=msg)
        else:
            if formAluno.validate_on_submit():
                formAluno.save()
                return redirect(url_for('registrar_responsavel', cpf=cpf))
                # print(form.alunos.data)
                # print(form.alunos.data)
        
        return render_template('register/registrar_aluno.html', cpf=cpf, formAluno=formAluno, origem='aluno')
    
    return render_template('register/registrar_aluno.html')



@app.route('/registrar_professor/', methods=['GET', 'POST'])
# @login_required
def registrar_professor():
    form = ProfessorForm()



    if form.validate_on_submit():
        form.save()
        return redirect(url_for('registrar_professor'))
    
    return render_template('register/registrar_professor.html', form=form)


@app.route('/registrar_secretaria/', methods=['GET', 'POST'])
# @login_required
def registrar_secretaria():
    form = SecretariaForm()



    if form.validate_on_submit():
        form.save()
        return redirect(url_for('registrar_secretaria'))
    
    return render_template('register/registrar_secretaria.html', form=form)



@app.route('/registrar_responsavel/', methods=['GET', 'POST'])
# @login_required
def registrar_responsavel():
    FormRespUser = RespUserForm()
    cpf = request.args.get('cpf') or request.form.get('cpf')
    origem = request.args.get('origem') or None 

    aluno = Aluno.query.filter_by(cpf=cpf).first()
    if cpf:
        if not aluno:
            msg = 'Aluno não encontrado!'
            return render_template('register/registrar_responsavel.html', cpf=cpf, msg=msg)
        
    elif FormRespUser.validate_on_submit():
        responsavel = FormRespUser.save()
        aluno = Aluno.query.filter_by(cpf=cpf).first()
        responsavel.alunos.append(aluno)
        db.session.commit()
        return redirect(url_for('registrar_responsavel'))
    
    return render_template('register/registrar_responsavel.html', FormRespUser=FormRespUser, cpf=cpf)



