
from app import app, db
from flask import Response, render_template, send_file, url_for, request, redirect, abort, session
from app.models import User, TipoUsuario
from app.forms import AlunoForm, ProfessorForm, UserForm, LoginForm

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


    if form.validate_on_submit():
        form.save()
        return redirect(url_for('login'))
    
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
    form = AlunoForm()


    if form.validate_on_submit():
        form.save()
        return redirect(url_for('login'))
    
    return render_template('register/registrar_aluno.html', form=form)



@app.route('/registrar_professor', methods=['GET', 'POST'])
# @login_required
def registrar_professor():
    form = ProfessorForm()


    if form.validate_on_submit():
        form.save()
        return redirect(url_for('login'))
    
    return render_template('register/registrar_professor.html', form=form)