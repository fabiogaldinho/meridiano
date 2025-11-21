# Imagem base oficial do Python
FROM python:3.11-slim


# Ver logs imediatamente e impedimento do python criar arquivos de versões compiladas
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


# Criação de usuário non-root para a produção com UIDs a partir de mil para usuários reais
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser


# Cria diretório da aplicação
RUN mkdir -p /app


# Define /app como diretório de trabalho
WORKDIR /app


# Instala dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# Cópia e execução do 'requirements.txt'
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn


# Copiar o resto da aplicação
COPY . .


# Cria diretórios necessaŕios pra aplicação
RUN mkdir -p /app/feeds /app/data


# Copia o script de entrypoint para o container
COPY entrypoint.sh /app/entrypoint.sh


# Define o script como executável
RUN chmod +x /app/entrypoint.sh


# Mudança para usuário appuser
RUN chown -R appuser:appuser /app

USER appuser


# Porta padrão do Gunicorn
EXPOSE 8000


# Roda o script de entrypoint
CMD ["/app/entrypoint.sh"]