# Multi-stage Dockerfile para FastAPI Backend
FROM python:3.11-slim as base

# Configurações de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Configurar diretório de trabalho
WORKDIR /app

# Instalar Poetry
RUN pip install poetry==$POETRY_VERSION
RUN poetry config virtualenvs.create false

# Copiar arquivos de dependências
COPY pyproject.toml ./
COPY poetry.lock* ./

# Stage de desenvolvimento
FROM base as development

# Instalar dependências de desenvolvimento
RUN poetry install --with dev,test

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p storage/attachments storage/import_examples logs

# Ajustar permissões
RUN chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Comando padrão para desenvolvimento
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage de produção
FROM base as production

# Instalar apenas dependências de produção
RUN poetry install --only=main --no-dev

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p storage/attachments storage/import_examples logs

# Ajustar permissões
RUN chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Comando para produção
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
