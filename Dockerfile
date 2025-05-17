# Imagen base de Python 3.13 en Alpine
FROM python:3.13-alpine

# Crea usuario sin privilegios
RUN adduser -D appuser

# Instala dependencias necesarias para compilar algunos paquetes (ej. psycopg2, cryptography)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    libpq

# Establece el directorio de trabajo
WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la app
COPY . .

# Cambia al usuario sin privilegios
USER appuser

# Expone el puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
