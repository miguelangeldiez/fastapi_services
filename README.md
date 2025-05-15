---

## 🐳 Ejecución con Docker

Este proyecto está preparado para ejecutarse fácilmente en contenedores Docker, utilizando **Docker Compose** para orquestar los servicios principales: la aplicación FastAPI y la base de datos PostgreSQL.

### 1. **Requisitos previos**
- **Docker** y **Docker Compose** instalados en tu sistema.
- Certificados TLS de desarrollo ya incluidos en el directorio `certs/` (no es necesario generarlos manualmente).

### 2. **Variables de entorno**
Asegúrate de tener un archivo `.env` en la raíz del proyecto con las siguientes variables (puedes personalizarlas según tus necesidades):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=threadfit_data
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres-db:5432/threadfit_data
JWT_SECRET_KEY=tu_clave_supersecreta
JWT_LIFETIME_SECONDS=3600
ALLOWED_ORIGINS=https://localhost:8000/
COOKIE_NAME=threadfit_cookie
```

> **Nota:** El servicio de la app espera conectarse a la base de datos en el host `postgres-db` (según el `docker-compose.yaml`).

### 3. **Construcción y ejecución**
Desde la raíz del proyecto, ejecuta:

```bash
docker-compose up --build
```

Esto construirá la imagen de la aplicación (usando Python 3.13-slim y todas las dependencias necesarias) y levantará ambos servicios:
- **python-app** (FastAPI): expuesto en [https://localhost:8000](https://localhost:8000) con TLS usando los certificados de `certs/`.
- **postgres-db** (PostgreSQL): accesible solo dentro de la red de Docker.

### 4. **Puertos expuestos**
- **8000:** API FastAPI (HTTPS)

### 5. **Configuraciones especiales**
- La aplicación se ejecuta en modo desarrollo con recarga automática (`--reload`) y utiliza los certificados TLS incluidos.
- Los datos de PostgreSQL se almacenan de forma persistente en el volumen `pgdata`.
- Si necesitas modificar los certificados, reemplaza los archivos en el directorio `certs/`.

---
