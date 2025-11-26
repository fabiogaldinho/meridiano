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
    opcao = 2

    if opcao == 1:    
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


        try:
            print("Adicionando nova coluna 'url_encoding'!")

            session.exec(text('ALTER TABLE articles ADD COLUMN url_encoding TEXT'))
            session.exec(text('UPDATE articles SET url_encoding = url'))

            session.commit()
        
        except Exception as e:
            print(f'Erro ao tentar adicionar a nova coluna url_encoding: {e}\n')
        
        print("Nova coluna 'url_encoding' adicionada com sucesso!\n")


        try:
            print("Desaplicando URL encoding.")
            col_url = Article.url

            for old, new in replaces:
                col_url = func.replace(col_url, new, old)
            
            stmt = update(Article).values(url=col_url)
            session.exec(stmt)
            session.commit()

        except Exception as e:
            print(f'Erro ao tentar desaplicar URL encoding: {e}\n')
        
        print("URL encoding desaplicado com sucesso!\n")
    

    else:
        try:
            print("Adicionando nova coluna 'marreta'!")

            session.exec(text('ALTER TABLE articles ADD COLUMN marreta BOOLEAN DEFAULT 0'))

            session.commit()
        
        except Exception as e:
            print(f'Erro ao tentar adicionar a nova coluna marreita: {e}\n')
        
        print("Nova coluna 'marreta' adicionada com sucesso!\n")