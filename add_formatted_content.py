#!/usr/bin/env python3
"""
Script de migração: adiciona coluna formatted_content
"""
from db import get_session
from sqlalchemy import text

print('=== Migração: Adicionando formatted_content ===\n')

with get_session() as session:
    try:
        # SQLite syntax
        session.exec(text('ALTER TABLE articles ADD COLUMN formatted_content TEXT'))
        session.commit()
        print('✅ Coluna formatted_content adicionada com sucesso!\n')
    except Exception as e:
        error_msg = str(e).lower()
        if 'duplicate column' in error_msg or 'already exists' in error_msg:
            print('ℹ️  Coluna formatted_content já existe, pulando...\n')
        else:
            print(f'❌ Erro ao adicionar coluna: {e}\n')
            raise

print('Migração concluída!')