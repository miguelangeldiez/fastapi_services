# Dockerfile

# Imagen base liviana con Python 3.13 y herramientas necesarias
FROM python:3.13-alpine

# Instala dependencias del sistema necesarias (psycopg, build)
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

# Establece directorio de trabajo
WORKDIR /app

# Copia dependencias
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY . .

# Asegúrate de que los certificados estén en el contenedor
COPY server.key /app/server.key
COPY server.pem /app/server.pem

# Establece permisos de solo lectura para los certificados
RUN chmod 400 /app/server.key /app/server.pem

# Expone el puerto para FastAPI
EXPOSE 8000

# Comando por defecto para levantar el microservicio con HTTPS
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/certs/localhost-key.pem", "--ssl-certfile", "/certs/localhost.pem", "--reload"]
