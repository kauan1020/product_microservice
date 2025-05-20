FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1
# Força TLS 1.2 como mínimo
ENV OPENSSL_CONF=/etc/ssl/openssl-mongodb.cnf

WORKDIR /app

# Instalar dependências do sistema com foco no OpenSSL atualizado
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    openssl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar OpenSSL explicitamente para MongoDB
RUN echo "[system_default_sect]\nMinProtocol = TLSv1.2\nCipherString = DEFAULT@SECLEVEL=1\n[ssl_conf]\nsystem_default = system_default_sect" > /etc/ssl/openssl-mongodb.cnf

# Primeiro, copie apenas os arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Instalar poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Garantir que temos o certifi e pymongo atualizados
RUN pip install --upgrade pip
RUN pip install --no-cache-dir certifi==2024.2.2 pymongo[srv]==4.6.1

# Instalar dependências do projeto
RUN poetry install --no-root --no-interaction --no-ansi

# Verificar instalações
RUN pip freeze | grep -E 'certifi|pymongo'

# Agora copie o resto da aplicação
COPY . .

RUN pwd && ls -l /app

EXPOSE 8002

CMD ["sh", "-c", "cd /app && poetry run uvicorn --host 0.0.0.0 --port 8002 tech.api.app:app"]