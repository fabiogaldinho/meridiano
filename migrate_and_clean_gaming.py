#!/usr/bin/env python3
"""
Script de migração e limpeza para o banco de dados Meridiano.
Adiciona campo briefing_analyzed e limpa dados antigos de gaming.
"""

from models import get_session, Article, Brief
from datetime import datetime, timedelta
from sqlmodel import select, and_
from sqlalchemy import text
import json

print('=== Migração e Limpeza do Banco de Dados ===\n')

with get_session() as session:
    # 1. Adicionar nova coluna briefing_analyzed (SQLite)
    print('1. Adicionando campo briefing_analyzed...')
    try:
        session.exec(text('ALTER TABLE articles ADD COLUMN briefing_analyzed BOOLEAN DEFAULT 0'))
        session.commit()
        print('   ✓ Campo briefing_analyzed adicionado com sucesso\n')
    except Exception as e:
        if 'duplicate column name' in str(e).lower():
            print('   ℹ Campo briefing_analyzed já existe, pulando...\n')
        else:
            print(f'   ✗ Erro ao adicionar campo: {e}\n')
            raise
    
    # 2. Criar índice para performance (SQLite)
    print('2. Criando índice para performance...')
    try:
        session.exec(text('CREATE INDEX IF NOT EXISTS idx_articles_briefing_analyzed ON articles(briefing_analyzed)'))
        session.commit()
        print('   ✓ Índice criado com sucesso\n')
    except Exception as e:
        print(f'   ⚠ Aviso: {e}\n')
    
    # 3. Deletar briefings de gaming
    print('3. Deletando briefings de gaming...')
    stmt_briefs = select(Brief).where(Brief.feed_profile == 'gaming')
    old_briefs = session.exec(stmt_briefs).all()
    
    brief_count = len(old_briefs)
    for brief in old_briefs:
        session.delete(brief)
    
    session.commit()
    print(f'   ✓ Deletados {brief_count} briefing(s) de gaming\n')
    
    # 4. Deletar artigos de gaming mais velhos que 7 dias
    print('4. Deletando artigos antigos de gaming (>7 dias)...')
    cutoff = datetime.now() - timedelta(days=7)
    print(f'   Data de corte: {cutoff.strftime("%Y-%m-%d %H:%M:%S")}')
    
    stmt_old = select(Article).where(
        and_(
            Article.feed_profile == 'gaming',
            Article.published_date < cutoff
        )
    )
    old_articles = session.exec(stmt_old).all()
    
    old_count = len(old_articles)
    for article in old_articles:
        session.delete(article)
    
    session.commit()
    print(f'   ✓ Deletados {old_count} artigo(s) antigo(s)\n')
    
    # 5. Limpar brief_ids e briefing_analyzed dos artigos recentes de gaming
    print('5. Limpando brief_ids e briefing_analyzed dos artigos recentes...')
    stmt_recent = select(Article).where(
        and_(
            Article.feed_profile == 'gaming',
            Article.published_date >= cutoff
        )
    )
    recent_articles = session.exec(stmt_recent).all()
    
    recent_count = len(recent_articles)
    for article in recent_articles:
        article.brief_ids = None
        article.briefing_analyzed = False
        session.add(article)
    
    session.commit()
    print(f'   ✓ Limpados {recent_count} artigo(s) recente(s)\n')
    
    # 6. Atualizar processed_at para agora (para entrar na janela de briefing)
    print('6. Atualizando processed_at dos artigos recentes para agora...')
    for article in recent_articles:
        if article.processed_at:  # Só atualiza se já foi processado
            article.processed_at = datetime.now()
            session.add(article)
    
    session.commit()
    print(f'   ✓ Atualizados {recent_count} artigo(s)\n')

print('=' * 50)
print('=== Migração e Limpeza Concluídas com Sucesso ===')
print('=' * 50)
print(f'\nResumo:')
print(f'  ✓ Campo briefing_analyzed adicionado')
print(f'  ✓ Índice de performance criado')
print(f'  ✓ {brief_count} briefing(s) deletado(s)')
print(f'  ✓ {old_count} artigo(s) antigo(s) deletado(s)')
print(f'  ✓ {recent_count} artigo(s) recente(s) limpos e prontos')
print(f'\nPróximo passo:')
print(f'  docker exec -it meridiano python run_briefing.py --feed gaming --generate-brief')
print()