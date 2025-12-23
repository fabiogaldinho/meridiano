#!/usr/bin/env python3
"""
Diagnóstico de imagens nos artigos e briefings do Meridiano
"""

from models import Article, Brief
from db import get_session
from sqlmodel import select, func, and_
import json

# Abre uma sessão do banco
session = get_session()

print("="*70)
print("DIAGNÓSTICO DE IMAGENS - MERIDIANO")
print("="*70 + "\n")

# ==========================================
# DIAGNÓSTICO 1: Quantos artigos têm imagem?
# ==========================================
print("1. ESTATÍSTICAS GERAIS DE ARTIGOS\n")

total_artigos = session.exec(select(func.count(Article.id))).one()
print(f"Total de artigos: {total_artigos}")

artigos_com_imagem = session.exec(
    select(func.count(Article.id))
    .where(
        and_(
            Article.image_url.is_not(None),  # type: ignore
            Article.image_url != ''           # type: ignore
        )
    )
).one()
print(f"Artigos COM imagem: {artigos_com_imagem}")
print(f"Artigos SEM imagem: {total_artigos - artigos_com_imagem}")
if total_artigos > 0:
    print(f"Porcentagem com imagem: {(artigos_com_imagem / total_artigos * 100):.1f}%")

print("\n" + "="*70 + "\n")

# ==========================================
# DIAGNÓSTICO 2: Por feed profile
# ==========================================
print("2. IMAGENS POR FEED PROFILE\n")

feeds = session.exec(select(Article.feed_profile).distinct()).all()

for feed in feeds:
    total = session.exec(
        select(func.count(Article.id))
        .where(Article.feed_profile == feed)
    ).one()
    
    com_img = session.exec(
        select(func.count(Article.id))
        .where(
            and_(
                Article.feed_profile == feed,
                Article.image_url.is_not(None),  # type: ignore
                Article.image_url != ''           # type: ignore
            )
        )
    ).one()
    
    if total > 0:
        print(f"  {feed:20s}: {com_img:4d}/{total:4d} ({com_img/total*100:5.1f}%)")
    else:
        print(f"  {feed:20s}: 0/0")

print("\n" + "="*70 + "\n")

# ==========================================
# DIAGNÓSTICO 3: Briefings e suas imagens
# ==========================================
print("3. ANÁLISE DOS ÚLTIMOS 10 BRIEFINGS\n")

# Pega os últimos 10 briefings
briefs = session.exec(
    select(Brief)
    .order_by(Brief.generated_at.desc())  # type: ignore
    .limit(10)
).all()

for brief in briefs:
    print(f"Briefing #{brief.id} ({brief.feed_profile}) - {brief.generated_at}:")
    
    # Pega os IDs dos artigos deste briefing
    try:
        article_ids = json.loads(brief.contributing_article_ids)
        print(f"  - {len(article_ids)} artigos no total")
        
        # Quantos têm imagem?
        artigos = session.exec(
            select(Article)
            .where(Article.id.in_(article_ids))  # type: ignore
        ).all()
        
        com_imagem = [a for a in artigos if a.image_url and a.image_url != '']
        print(f"  - {len(com_imagem)} artigos COM imagem")
        
        if com_imagem:
            # Mostra o de maior impact
            top_article = max(com_imagem, key=lambda x: x.impact_score or 0)
            print(f"  - Maior impact com imagem: {top_article.impact_score}/10 (ID {top_article.id})")
            print(f"  - URL: {top_article.image_url[:80]}...")
        else:
            print(f"  - ⚠️  NENHUM artigo tem imagem!")
        
    except Exception as e:
        print(f"  - ❌ Erro ao processar: {e}")
    
    print()

print("="*70)

session.close()