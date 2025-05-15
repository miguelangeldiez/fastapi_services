# 🧵 ThreadFit - Microservicio de Autenticación y Generación de Datos Sintéticos

Este proyecto es un microservicio desarrollado con **FastAPI** que forma parte del ecosistema **ThreadFit**. Su objetivo principal es gestionar la autenticación de usuarios y proporcionar herramientas para la generación de datos sintéticos, como usuarios, publicaciones y comentarios.

---

## 🚀 Características Principales

### 1. **Autenticación de Usuarios**
- Registro y login de usuarios utilizando **JWT** almacenados en cookies seguras.
- Gestión de usuarios activos, superusuarios y verificados.
- Implementación basada en **FastAPI Users**.

### 2. **Generación de Datos Sintéticos**
- Generación de usuarios, publicaciones y comentarios ficticios.
- Exportación de datos en formatos **JSON**, **CSV** y **PDF**.
- Soporte para generación en tiempo real mediante **WebSockets**.

### 3. **Gestión de Perfiles**
- Visualización de perfiles de usuario.
- Listado de publicaciones asociadas a un usuario.

### 4. **Interacciones**
- Publicación de comentarios en publicaciones.
- Gestión de likes en publicaciones.

---

## 📂 Estructura del Proyecto

```
.
├── app/
│   ├── db/                # Configuración y modelos de la base de datos
│   ├── routes/            # Rutas de la API (autenticación, publicaciones, interacciones, etc.)
│   ├── synthetic_data/    # Lógica para generación de datos sintéticos
│   └── __init__.py        # Inicialización del módulo
├── tests/                 # Pruebas automatizadas
├── alembic/               # Migraciones de la base de datos
├── certs/                 # Certificados TLS para desarrollo
├── .vscode/               # Configuración de Visual Studio Code
├── .env                   # Variables de entorno
├── docker-compose.yaml    # Configuración de Docker Compose
├── Dockerfile             # Configuración del contenedor Docker
├── main.py                # Punto de entrada de la aplicación
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Documentación del proyecto
```

---

## ⚙️ Configuración del Entorno

### 1. **Variables de Entorno**
Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
JWT_SECRET_KEY=tu_clave_supersecreta
JWT_LIFETIME_SECONDS=3600

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=threadfit_data

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/threadfit_data
ALLOWED_ORIGINS=https://localhost:8000/
COOKIE_NAME=threadfit_cookie
```

### 2. **Instalación**
1. Clona el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd threadfit
   ```
2. Construye e inicia los servicios con Docker:
   ```bash
   docker-compose up --build
   ```
3. Accede al servicio en: [https://localhost:8000/docs](https://localhost:8000/docs)

---

## 🧪 Pruebas

El proyecto incluye pruebas automatizadas para garantizar la calidad del código. Para ejecutarlas:

1. Instala las dependencias de desarrollo:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta las pruebas con `pytest`:
   ```bash
   pytest
   ```

---

## 📜 Endpoints Principales

### **Autenticación**
- `POST /auth/register`: Registro de usuarios.
- `POST /auth/login`: Login de usuarios.

### **Publicaciones**
- `POST /posts/create_post`: Crear una publicación.
- `GET /posts/all_posts`: Listar publicaciones paginadas.

### **Interacciones**
- `POST /interactions/{post_id}/comments`: Comentar en una publicación.
- `POST /interactions/{post_id}/like`: Dar like a una publicación.

### **Datos Sintéticos**
- `POST /synthetic/users`: Generar usuarios ficticios.
- `POST /synthetic/posts`: Generar publicaciones ficticias.
- `POST /synthetic/comments`: Generar comentarios ficticios.
- `GET /data/users`: Exportar usuarios generados.
- `GET /data/posts`: Exportar publicaciones generadas.
- `GET /data/comments`: Exportar comentarios generados.

---

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework principal para la API.
- **SQLAlchemy**: ORM para la base de datos.
- **PostgreSQL**: Base de datos relacional.
- **Docker**: Contenerización del proyecto.
- **Faker**: Generación de datos ficticios.
- **pytest**: Pruebas automatizadas.

---

## 📝 Notas Adicionales

- El proyecto utiliza **TLS** para el entorno de desarrollo. Los certificados se encuentran en el directorio `certs/`.
- Las migraciones de la base de datos se gestionan con **Alembic**.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, abre un issue o envía un pull request si deseas colaborar.

---

## 📧 Contacto

Si tienes preguntas o sugerencias, no dudes en contactarme en: miguelangeldiezbeltran@gmail.com
