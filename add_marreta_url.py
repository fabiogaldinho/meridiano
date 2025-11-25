from models import Article, get_session
from sqlalchemy import text
from sqlmodel import update, func


replaces = [
    ("/", "%2F"),
    (":", "%3A"),
    (" ", "%20"),
    ("?", "%3F"),
    ("&", "%26"),
    ("=", "%3D"),
    ("#", "%23")
]

with get_session() as session:
    try:
        print("Aplicando URL encoding.")
        col_url = Article.url

        for old, new in replaces:
            col_url = func.replace(col_url, old, new)
        
        stmt = update(Article).values(url=col_url)
        session.exec(stmt)
        session.commit()

    except Exception as e:
        print(f'Erro ao tentar aplicar URL encoding: {e}\n')
    
    print("URL encoding aplicado com sucesso!\n")


    try:
        print("Adicionando Marreta ao URL.")

        session.exec(text("UPDATE articles SET url = CONCAT('https://marreta.galdinho.news/p/',url);"))
        session.commit()

    except Exception as e:
        print(f'Erro ao tentar concatenar URL do Marreta: {e}\n')
    
    print("URL do Marreta concatenado com sucesso!\n")