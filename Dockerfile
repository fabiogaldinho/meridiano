############################
# STAGE 1 — FRONTEND BUILD
############################
FROM node:20-alpine AS frontend-build

WORKDIR /frontend

# Copia apenas o necessário pra instalar deps
COPY frontend/package*.json ./
RUN npm ci

# Copia o resto do frontend
COPY frontend/ ./

# Build do React
RUN npm run build


############################
# STAGE 2 — BACKEND
############################
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Usuário non-root
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Backend
COPY . .

# Copia SOMENTE o build do frontend
COPY --from=frontend-build /frontend/dist /app/frontend/dist

# Diretórios necessários
RUN mkdir -p /app/feeds /app/data

# Entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Permissões
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["/app/entrypoint.sh"]