# 🛡️ Auth Service - ThreadFit

Microservicio de autenticación basado en **FastAPI** con soporte completo para:
- Registro de usuarios
- Login vía JWT en cookies
- Validación de tokens
- Gestión de usuarios activos, superusuarios y verificados

Este servicio forma parte del ecosistema de microservicios de **ThreadFit** 🧵💪

---

## 🚀 Tecnologías utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [fastapi-users](https://frankie567.github.io/fastapi-users/)
- PostgreSQL (vía Docker)
- SQLAlchemy 2.0 (modo asíncrono)
- Pydantic 2.x + pydantic-settings
- JWT con almacenamiento en cookies seguras
- Docker & Docker Compose

---

## ⚙️ Configuración del entorno

### Variables de entorno `.env`

```env
JWT_SECRET_KEY=tu_clave_supersecreta
JWT_LIFETIME_SECONDS=3600

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=threadfit_data

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/threadfit_data
