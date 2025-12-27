#!/usr/bin/env python3
"""
Migração: Cria tabela users
"""
from db import get_session
from sqlalchemy import text

print('=== Criando tabela users ===\n')

with get_session() as session:
    try:
        # SQLite syntax
        session.exec(text('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                preferences TEXT
            )
        '''))
        
        # Criar índices
        session.exec(text('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)'))
        session.exec(text('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)'))
        
        session.commit()
        print('✅ Tabela users criada com sucesso!\n')
    except Exception as e:
        print(f'❌ Erro: {e}\n')
        raise

print('Migração concluída!')