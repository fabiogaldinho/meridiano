#!/bin/bash
# Script de entrypoint para inicializar o banco de dados e iniciar o Gunicorn

set -e 

echo "Inicializando banco de dados..."
python -c "import database; database.init_db()"

echo "Banco de dados inicializado com sucesso!"
echo "Iniciando Gunicorn..."


exec gunicorn --bind 0.0.0.0:8000 \
              --workers 2 \
              --timeout 120 \
              --access-logfile - \
              --error-logfile - \
              app:app