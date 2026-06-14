# app/auth/routes.py
from flask import Blueprint, render_template, redirect, session, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from flask import current_app
import secrets
from datetime import datetime
import os

auth_bp = Blueprint('auth', __name__)

# Configuração OAuth
oauth = OAuth(current_app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url=os.getenv('GOOGLE_DISCOVERY_URL'),
    client_kwargs={'scope': 'openid email profile'}
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.admin:
            return redirect(url_for('admin.dashboard'))
        print("Usuário já autenticado:", current_user.nome)  # Debug: Verificar o nome do usuário autenticado
        return redirect(url_for('cliente.painel'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.senha and user.check_senha(senha):
            login_user(user)
            print("Usuário autenticado com sucesso:", user.nome)  # Debug: Verificar o nome do usuário autenticado
            flash('Login realizado com sucesso!', 'success')
            
            if user.admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('cliente.painel'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('cliente.painel'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('auth.registro'))
        
        user = User(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            email=email,
            senha=generate_password_hash(senha),
            admin=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        print("Novo usuário registrado e autenticado:", user.nome)  # Debug: Verificar o nome do novo usuário registrado
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('cliente.painel'))
    
    return render_template('auth/registro.html')

@auth_bp.route('/login-google')
def login_google():
    redirect_uri = url_for('auth.google_callback', _external=True)
    print(redirect_uri)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/google-callback', methods=['GET', 'POST'])
def google_callback():
    token = google.authorize_access_token()  # Debug: Verificar o token recebido
    user_info = google.userinfo()  # Debug: Verificar as informações do usuário retornadas
    print("Informações do usuário do Google:", user_info)  # Debug: Verificar as informações do usuário
    email = user_info['email']
    nome = user_info.get('name', '')
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        user = User(
            nome=nome,
            email=email,
            google_id=user_info['sub'],
            telefone='',
            admin=False
        )
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso via Google!', 'success')
    
    login_user(user)
    print("Usuário autenticado via Google:", user.nome)  # Debug: Verificar o nome do usuário autenticado via Google
    
    if user.admin:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('cliente.painel'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('main.landing'))