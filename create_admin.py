#!/usr/bin/env python3
"""
Script para criar usuário admin inicial
"""
from models import User
from db import get_session
from utils_auth import hash_password
import sys

print('=== Criar Usuário Admin ===\n')

username = input('Username: ').strip()
email = input('Email: ').strip()
password = input('Senha: ').strip()
full_name = input('Nome completo (opcional): ').strip()

if not username or not email or not password:
    print('❌ Username, email e senha são obrigatórios!')
    sys.exit(1)

if len(password) < 6:
    print('❌ Senha deve ter pelo menos 6 caracteres!')
    sys.exit(1)

with get_session() as session:
    # Verificar se já existe
    from sqlmodel import select
    existing = session.exec(
        select(User).where(User.username == username)
    ).first()
    
    if existing:
        print(f'❌ Username "{username}" já existe!')
        sys.exit(1)
    
    # Criar admin
    admin = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name if full_name else None,
        is_active=True,
        is_admin=True  # ✅ Admin!
    )
    
    session.add(admin)
    session.commit()
    session.refresh(admin)
    
    print(f'\n✅ Admin criado com sucesso!')
    print(f'   ID: {admin.id}')
    print(f'   Username: {admin.username}')
    print(f'   Email: {admin.email}')