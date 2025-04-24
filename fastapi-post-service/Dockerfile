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
COPY ./app ./app

# Expone el puerto para FastAPI
EXPOSE 8000

# Comando por defecto para levantar el microservicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
