# ThreadFit

API de ejemplo para gestión de publicaciones, usuarios y generación de datos sintéticos, lista para despliegue en Docker y Kubernetes con autoescalado (HPA).

---

## 🚀 Características principales

- **FastAPI** con autenticación JWT y cookies seguras.
- **PostgreSQL** como base de datos principal.
- **Generación de datos sintéticos** (usuarios, posts, comentarios).
- **WebSockets** para generación en tiempo real.
- **Exportación de datos** en JSON, CSV y PDF.
- **Preparado para despliegue en Docker y Kubernetes**.
- **Autoescalado con HPA** (Horizontal Pod Autoscaler) en Kubernetes.
- **Certificados TLS de desarrollo incluidos**.

---

## 🐳 Ejecución local con Docker Compose

### 1. Requisitos previos

- Docker y Docker Compose instalados.
- Certificados TLS de desarrollo en el directorio `certs/` (ya incluidos).

### 2. Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con:

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

> **Nota:** El servicio espera conectarse a la base de datos en el host `postgres-db`.

### 3. Construcción y ejecución

```bash
docker-compose up --build
```

Esto levantará:

- **fastapi-server** (FastAPI): [https://localhost:8000](https://localhost:8000)
- **postgres-db** (PostgreSQL): solo accesible en la red interna de Docker.

### 4. Puertos expuestos

- **8000:** API FastAPI (HTTPS)

### 5. Persistencia y certificados

- Los datos de PostgreSQL se almacenan en el volumen `pgdata`.
- Los certificados TLS están en `certs/`.

---

## ☸️ Despliegue en Kubernetes (con HPA)

### 1. Requisitos previos

- Un clúster Kubernetes (Minikube, Kind, GKE, etc.).
- `kubectl` configurado.
- (Opcional) `minikube` para pruebas locales.

### 2. Archivos de despliegue

- Manifiestos en `k8s/`:
  - `deployments.yaml`: despliegue de FastAPI y PostgreSQL.
  - `services.yaml`: servicios para exponer la API y la base de datos.
  - `ingress.yaml`: acceso externo vía Ingress (TLS).
  - `hpa.yaml`: configuración de autoescalado horizontal.
  - `secret.yaml`, `configmap.yaml`: configuración y secretos.

### 3. Despliegue rápido

```bash
./deploy.sh
```

Este script:
- Crea el namespace `threadfit`.
- Aplica todos los recursos de `k8s/`.
- Configura el HPA.
- Muestra el estado de los recursos.

### 4. Acceso y pruebas

- Añade en tu `/etc/hosts`:
  ```
  127.0.0.1 threadfit.local
  ```
- Accede a [https://threadfit.local](https://threadfit.local) en tu navegador.
- Para probar el HPA, genera carga con:
  ```bash
  kubectl run -i --tty load-generator --rm --image=busybox -- /bin/sh
  # Dentro del pod:
  while true; do wget -q -O- http://threadfit-service:8000/; done
  ```
- Observa el escalado con:
  ```bash
  kubectl get hpa -n threadfit
  kubectl get pods -n threadfit
  ```

---

## 🧪 Pruebas

- Ejecuta los tests con `pytest`:
  ```bash
  pytest
  ```

---

## 📂 Estructura del proyecto

```
app/
  config/
  db/
  real_time/
  routes/
  synthetic_data/
  ...
k8s/
certs/
tests/
main.py
compose.yaml
Dockerfile
...
```

---

## 📄 Notas adicionales

- La aplicación está configurada para desarrollo y producción.
- Puedes modificar los certificados en `certs/` para tu entorno.
- El autoescalado (HPA) requiere métricas habilitadas en tu clúster Kubernetes.

---

¡Listo para escalar y probar en local o en la nube! 🚀
