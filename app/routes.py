
from app import app, db
from flask import Response, render_template, send_file, url_for, request, redirect, abort, session
from app.models import User, TipoUsuario
from app.forms import UserForm, LoginForm

from sqlalchemy import desc

from openpyxl import Workbook
from io import BytesIO
import os

from flask_login import logout_user, login_user, current_user, login_required

from datetime import datetime, timezone

import csv



@app.route('/register_user/', methods=['GET', 'POST'])
# @login_required
def register():
    form = UserForm()


    if form.validate_on_submit():
        form.save()
        return redirect(url_for('login'))
    
    return render_template('register/register_user.html', form=form)



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
@login_required
def home():
 
    
    return render_template('home.html')
