# Imagen base oficial de Python 3.12 en su versión mínima
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Evita que Python escriba archivos .pyc y que bufferice la salida
# Importante para ver los logs en tiempo real en Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copia primero solo el fichero de dependencias
# Docker cachea esta capa: si no cambian las dependencias,
# no las reinstala en cada build. Ahorra mucho tiempo.
COPY pyproject.toml .

# Instala las dependencias (pyproject.toml lo completaremos en Fase 2)
# Por ahora instalamos solo lo mínimo para que el build no falle
RUN pip install --upgrade pip

# Copia el resto del código
COPY . .