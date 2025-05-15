# Dockerfile

# Imagen base liviana con Python 3.13 y herramientas necesarias
FROM python:3.13-alpine

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece directorio de trabajo
WORKDIR /app

# Copia dependencias
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY . .

# Expone el puerto para FastAPI
EXPOSE 8000

# Comando por defecto para levantar el microservicio con HTTPS
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/certs/localhost-key.pem", "--ssl-certfile", "/certs/localhost.pem", "--reload"]
