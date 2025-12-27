# utils_auth.py
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import wraps
from flask import request, jsonify

# Configurações
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DAYS = 30


def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )


def create_jwt_token(user_id: int, username: str, is_admin: bool = False) -> str:
    """Cria um JWT token."""
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decodifica e valida um JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido


def get_token_from_header() -> Optional[str]:
    """Extrai token do header Authorization."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    # Formato esperado: "Bearer <token>"
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


def login_required(f):
    """Decorator para proteger rotas (requer autenticação)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        payload = decode_jwt_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        # Adiciona payload ao request.user
        request.user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """Decorator para rotas que exigem admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        payload = decode_jwt_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        if not payload.get('is_admin'):
            return jsonify({'error': 'Acesso negado: requer privilégios de admin'}), 403
        
        request.user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function