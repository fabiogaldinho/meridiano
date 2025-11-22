#!/usr/bin/env python3
"""
Script de limpeza única para identificar e marcar artigos truncados
que ainda não foram processados.

Uso: python cleanup_truncated_articles.py
"""

from datetime import datetime
from models import Article, get_session
from sqlmodel import select, and_
import sys

# Mesmas constantes de validação que usamos no scraping
MIN_CONTENT_LENGTH = 500

# Indicadores comuns de paywall
PAYWALL_INDICATORS = [
    'subscribe to continue reading',
    'this content is for subscribers',
    'sign up to read more',
    'become a member to',
    'subscribe for full access',
    'continue reading for',
]

def check_content_quality(raw_content):
    """
    Verifica se o conteúdo de um artigo parece ser de boa qualidade.
    
    Retorna:
        tuple: (is_valid, reason)
        - is_valid (bool): True se o conteúdo passou nas verificações
        - reason (str): Explicação de por que falhou (se falhou)
    """
    
    if not raw_content:
        return False, "No content"
    
    # Verificação 1: Conteúdo muito curto
    if len(raw_content) < MIN_CONTENT_LENGTH:
        return False, f"Too short ({len(raw_content)} chars)"
    
    # Verificação 2: Truncamento óbvio
    content_tail = raw_content[-50:].strip()
    last_char = content_tail[-1] if content_tail else ''
    
    if last_char.isalnum():
        last_words = content_tail.split()[-3:] if content_tail.split() else []
        
        if last_words and len(last_words[-1]) < 3 and len(raw_content) < 3000:
            return False, f"Appears truncated (ends: '...{content_tail[-30:]}')"
        
        if len(raw_content) < 2000:
            # Artigo curto terminando sem pontuação é suspeito, mas não fatal
            # Vamos deixar passar com um aviso
            pass
    
    # Verificação 3: Indicadores de paywall
    content_lower = raw_content[-200:].lower()
    for indicator in PAYWALL_INDICATORS:
        if indicator in content_lower:
            return False, f"Paywall detected ('{indicator}')"
    
    return True, "OK"


def cleanup_unprocessed_articles(dry_run=True):
    """
    Identifica artigos não processados com problemas de qualidade
    e os marca como filtrados.
    
    Args:
        dry_run (bool): Se True, apenas mostra o que seria feito sem fazer mudanças
    """
    
    print("=" * 80)
    print("CLEANUP: Identificando artigos truncados não processados")
    print("=" * 80)
    print()
    
    if dry_run:
        print("MODE: DRY RUN - Nenhuma mudança será feita no banco de dados")
        print()
    else:
        print("MODE: LIVE - Mudanças serão aplicadas ao banco de dados")
        print()
        # Pede confirmação em modo live
        confirmation = input("Tem certeza que deseja prosseguir? Digite 'SIM' para confirmar: ")
        if confirmation != "SIM":
            print("Operação cancelada pelo usuário.")
            return
        print()
    
    # Busca artigos não processados
    with get_session() as session:
        statement = select(Article).where(
            and_(
                Article.processed_at.is_(None),
                Article.raw_content.is_not(None),
                Article.raw_content != ""
            )
        )
        
        unprocessed_articles = session.exec(statement).all()
        total_articles = len(unprocessed_articles)
        
        print(f"Encontrados {total_articles} artigos não processados para verificar")
        print()
        
        if total_articles == 0:
            print("Nenhum artigo para verificar. Limpeza concluída.")
            return
        
        # Contadores para estatísticas
        problematic_articles = []
        valid_articles = 0
        
        # Verifica cada artigo
        print("Verificando qualidade do conteúdo...")
        print("-" * 80)
        
        for article in unprocessed_articles:
            is_valid, reason = check_content_quality(article.raw_content)
            
            if not is_valid:
                problematic_articles.append({
                    'id': article.id,
                    'url': article.url,
                    'title': article.title,
                    'feed_profile': article.feed_profile,
                    'content_length': len(article.raw_content) if article.raw_content else 0,
                    'reason': reason
                })
                print(f"  ✗ ID {article.id}: {reason}")
                print(f"    Profile: [{article.feed_profile}]")
                print(f"    Title: {article.title[:70]}...")
                print()
            else:
                valid_articles += 1
        
        print("-" * 80)
        print()
        
        # Mostra estatísticas
        print("RESUMO:")
        print(f"  Total verificado: {total_articles}")
        print(f"  Artigos válidos: {valid_articles}")
        print(f"  Artigos problemáticos: {len(problematic_articles)}")
        print()
        
        if len(problematic_articles) == 0:
            print("Nenhum artigo problemático encontrado. Limpeza concluída.")
            return
        
        # Agrupa por razão para estatísticas detalhadas
        reasons = {}
        for article in problematic_articles:
            reason_key = article['reason'].split('(')[0].strip()  # Pega só a parte principal
            reasons[reason_key] = reasons.get(reason_key, 0) + 1
        
        print("Problemas encontrados por tipo:")
        for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {reason}: {count}")
        print()
        
        # Se não é dry run, aplica as mudanças
        if not dry_run:
            print("Aplicando mudanças no banco de dados...")
            
            for article_info in problematic_articles:
                article = session.get(Article, article_info['id'])
                if article:
                    article.initial_filter_score = 1
                    session.add(article)
            
            session.commit()
            print(f"✓ {len(problematic_articles)} artigos marcados como filtrados")
        else:
            print("DRY RUN: Nenhuma mudança foi aplicada.")
            print("Execute novamente com --live para aplicar as mudanças.")
        
        print()
        print("=" * 80)
        print("Limpeza concluída")
        print("=" * 80)


if __name__ == "__main__":
    # Verifica se foi passado o argumento --live
    is_live = '--live' in sys.argv
    
    # Roda em modo dry-run por padrão, ou live se especificado
    cleanup_unprocessed_articles(dry_run=not is_live)