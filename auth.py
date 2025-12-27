# auth.py - Rotas de autenticação
from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlmodel import select
import os

from models import User
from db import get_session
from utils_auth import (
    hash_password,
    verify_password,
    create_jwt_token,
    login_required,
    admin_required
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Registra novo usuário (público, mas validado por whitelist).
    Diferente do /register que exige admin token.
    """
    data = request.get_json()
    
    # Validação básica
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Campos obrigatórios: username, email, password'}), 400
    
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    full_name = data.get('full_name', '').strip()
    
    # Validações
    if len(username) < 3:
        return jsonify({'error': 'Username deve ter pelo menos 3 caracteres'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
    
    if '@' not in email:
        return jsonify({'error': 'Email inválido'}), 400
    
    # ============================================
    # WHITELIST: Valida se e-mail está permitido
    # ============================================
    allowed_emails_str = os.getenv('ALLOWED_EMAILS', '')
    allowed_emails = [e.strip().lower() for e in allowed_emails_str.split(',') if e.strip()]
    
    if not allowed_emails:
        return jsonify({'error': 'Sistema de cadastro não configurado'}), 500
    
    if email not in allowed_emails:
        return jsonify({
            'error': 'E-mail não autorizado. Entre em contato com o administrador para solicitar acesso'
        }), 403
    
    # ============================================
    # Criar usuário (mesmo código do /register)
    # ============================================
    with get_session() as session:
        # Verificar se username já existe
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username já existe'}), 409
        
        # Verificar se email já existe
        existing_email = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if existing_email:
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Criar novo usuário (sempre com is_admin=False)
        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name if full_name else None,
            is_active=True,
            is_admin=False  # ← Sempre False no signup público
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        return jsonify({
            'message': 'Conta criada com sucesso! Você já pode fazer login.',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'full_name': new_user.full_name
            }
        }), 201


@auth_bp.route('/register', methods=['POST'])
@admin_required 
def register():
    """Registra um novo usuário (apenas admin)."""
    data = request.get_json()
    
    # Validação básica
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Campos obrigatórios: username, email, password'}), 400
    
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    full_name = data.get('full_name', '').strip()
    
    # Validações
    if len(username) < 3:
        return jsonify({'error': 'Username deve ter pelo menos 3 caracteres'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
    
    if '@' not in email:
        return jsonify({'error': 'Email inválido'}), 400
    
    with get_session() as session:
        # Verificar se username já existe
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username já existe'}), 409
        
        # Verificar se email já existe
        existing_email = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if existing_email:
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Criar novo usuário
        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name if full_name else None,
            is_active=True,
            is_admin=False
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'full_name': new_user.full_name
            }
        }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário."""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    with get_session() as session:
        # Buscar usuário
        user = session.exec(
            select(User).where(User.username == username)
        ).first()
        
        if not user:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Verificar se está ativo
        if not user.is_active:
            return jsonify({'error': 'Usuário desativado'}), 403
        
        # Verificar senha
        if not verify_password(password, user.password_hash):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Atualizar last_login
        user.last_login = datetime.now()
        session.add(user)
        session.commit()
        
        # Criar token
        token = create_jwt_token(
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin
            }
        }), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Retorna informações do usuário logado."""
    user_id = request.user['user_id']
    
    with get_session() as session:
        user = session.get(User, user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200


@auth_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """Lista todos os usuários (apenas admin)."""
    with get_session() as session:
        users = session.exec(select(User)).all()
        
        return jsonify({
            'users': [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'full_name': u.full_name,
                    'is_active': u.is_active,
                    'is_admin': u.is_admin,
                    'created_at': u.created_at.isoformat() if u.created_at else None,
                    'last_login': u.last_login.isoformat() if u.last_login else None
                }
                for u in users
            ]
        }), 200