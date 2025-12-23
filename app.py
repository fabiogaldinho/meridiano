# app.py - VERSÃO SPA REACT
from flask import Flask, send_from_directory, abort
from flask_cors import CORS
from db import create_db_and_tables
from api import api_bp
import os


# ============================================
# CONFIGURAÇÃO DO FLASK
# ============================================
app = Flask(
    __name__,
    static_folder=None
)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "a_default_secret_key_for_development_only"
)


# ============================================
# BLUEPRINTS
# ============================================
app.register_blueprint(api_bp)


# ============================================
# CORS
# ============================================
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://galdinho.news",      # Produção
            "http://localhost:5173"       # Dev
        ]
    }
})


# ============================================
# ROTAS DO SPA REACT
# ============================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    """
    Serve o SPA React para todas as rotas não-API.
    
    Lógica:
    1. Se o path é um arquivo estático (JS, CSS, etc) → serve o arquivo
    2. Senão → serve index.html (React Router pega a rota)
    """

    # se for rota de API, deixa o blueprint tratar (ou devolve 404)
    if path.startswith('api/'):
        abort(404)
    
    static_folder = os.path.join(app.root_path, 'frontend', 'dist')
    
    # Verificar se dist existe
    if not os.path.exists(static_folder):
        return """
        <h1>⚠️ Frontend não compilado</h1>
        <p>Execute os comandos:</p>
        <pre>
            cd frontend
            npm install
            npm run build
        </pre>
        """, 500
    
    # Se o path é um arquivo real (JS, CSS, imagens)
    file_path = os.path.join(static_folder, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(static_folder, path)
    
    # Senão, serve index.html (SPA catchall)
    return send_from_directory(static_folder, 'index.html')


# ============================================
# INICIALIZAÇÃO
# ============================================
if __name__ == '__main__':
    create_db_and_tables()
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )