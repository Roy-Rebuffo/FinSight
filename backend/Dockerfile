FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencias del sistema necesarias para compilar psycopg2 y otras libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiamos pyproject.toml primero para aprovechar la caché de Docker.
# Si no cambian las dependencias, Docker no las reinstala en cada build.
COPY pyproject.toml .

# Instalamos dependencias. El punto final instala el proyecto actual.
# --no-cache-dir reduce el tamaño de la imagen final.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

# Copiamos el resto del código después de instalar dependencias
COPY . .