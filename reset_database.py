# reset_database.py
"""
Script para resetar o banco de dados completamente.
USO: python reset_database.py
ATENÇÃO: Isso vai DELETAR TODOS OS DADOS! Use com cuidado.
"""

from sqlmodel import SQLModel
from models import engine, Article, Brief
import config_base as config

def reset_database():
    """Drop all tables and recreate them fresh."""
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print(f"\nDatabase URL: {config.DATABASE_URL}")
    print(f"\nThis will DELETE ALL DATA in the database.")
    
    # Pedir confirmação
    confirmation = input("\nType 'RESET' to confirm: ")
    
    if confirmation != "RESET":
        print("Reset cancelled. No changes made.")
        return
    
    print("\nDropping all existing tables...")
    # Isso remove todas as tabelas definidas nos models
    SQLModel.metadata.drop_all(engine)
    print("✓ All tables dropped")
    
    print("\nCreating fresh tables with new schema...")
    # Isso recria todas as tabelas com o schema atual
    SQLModel.metadata.create_all(engine)
    print("✓ All tables created")
    
    print("\n" + "=" * 60)
    print("DATABASE RESET COMPLETE")
    print("=" * 60)
    print("\nThe database is now empty and ready for fresh data.")
    print("Next step: Run 'python run_briefing.py --feed [nome_do_feed]' to populate.")

if __name__ == "__main__":
    reset_database()