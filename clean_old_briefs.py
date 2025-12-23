# Script: clean_old_briefs.py
from db import get_session
from models import Brief
from sqlmodel import select

with get_session() as session:
    briefs = session.exec(select(Brief)).all()
    
    for brief in briefs:
        # Remove tudo após a linha de separação
        if '---\n\n## Artigos de Referência' in brief.brief_markdown:
            clean_content = brief.brief_markdown.split('---\n\n## Artigos de Referência')[0]
            brief.brief_markdown = clean_content.rstrip()
            session.add(brief)
    
    session.commit()
    print(f'✅ Limpou {len(briefs)} briefings')