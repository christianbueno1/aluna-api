# 🐳 Comandos de Contenedor - Aluna API

> **ℹ️ Self-Contained Image**: Los modelos ML están incluidos en la imagen (~18KB).
> No necesitas montar volúmenes ni copiar archivos adicionales. ¡Pull y Run!

## 🏗️ Build de la imagen

```bash
# Build con Podman (recomendado)
podman build -t aluna-api:latest -f Containerfile .

# Build con Docker
docker build -t aluna-api:latest -f Containerfile .

# Build con tag específico
podman build -t aluna-api:1.0.0 -f Containerfile .

# Ver tamaño de la imagen
podman images aluna-api
```

## 🚀 Ejecutar el contenedor

### Producción (recomendado)
```bash
# Ejecutar directamente - todo incluido en la imagen
podman run -d \
  --name aluna-api \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  aluna-api:latest

# Verificar que está funcionando
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### Desarrollo (con hot reload)
```bash
# Montar solo código para desarrollo (modelos ya en imagen)
podman run -d \
  --name aluna-api-dev \
  -p 8000:8000 \
  -v $(pwd)/app:/app/app:ro \
  --env-file .env \
  aluna-api:latest \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Con base de datos (usando pod existente)
```bash
# Crear red compartida
podman network create aluna-network

# Conectar contenedor de DB a la red (si ya existe)
podman network connect aluna-network aluna-db

# Ejecutar API en la red
podman run -d \
  --name aluna-api \
  --network aluna-network \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://chris:maGazine1!@aluna-db:5432/chris_db" \
  --env-file .env \
  --restart unless-stopped \
  aluna-api:latest
```

## 🔍 Inspección y debugging

```bash
# Ver logs en tiempo real
podman logs -f aluna-api

# Ver últimas 100 líneas
podman logs --tail 100 aluna-api

# Entrar al contenedor
podman exec -it aluna-api /bin/bash

# Verificar que los modelos están presentes
podman exec aluna-api ls -lh /app/modelos_entrenados

# Ver recursos utilizados
podman stats aluna-api

# Inspeccionar configuración
podman inspect aluna-api

# Healthcheck manual
curl http://localhost:8000/health
```

## 🛑 Gestión del contenedor

```bash
# Detener
podman stop aluna-api

# Iniciar
podman start aluna-api

# Reiniciar
podman restart aluna-api

# Eliminar contenedor
podman rm -f aluna-api

# Ver todos los contenedores
podman ps -a

# Ver solo contenedores corriendo
podman ps
```

## 🧹 Limpieza

```bash
# Eliminar contenedor e imagen
podman rm -f aluna-api
podman rmi aluna-api:latest

# Limpiar imágenes no utilizadas
podman image prune -a

# Limpiar contenedores detenidos
podman container prune

# Limpiar todo (cuidado!)
podman system prune -a
```

## 📦 Distribución de imagen

### Export/Import (transferencia entre máquinas)
```bash
# Exportar imagen a archivo tar
podman save -o aluna-api.tar aluna-api:latest

# Comprimir para transferencia
gzip aluna-api.tar
# Resultado: aluna-api.tar.gz

# En otra máquina: importar imagen
podman load -i aluna-api.tar.gz

# Verificar que se importó
podman images aluna-api
```

### Push a Container Registry

#### Docker Hub
```bash
# Login
podman login docker.io

# Tag para tu usuario
podman tag aluna-api:latest christianbueno1/aluna-api:latest
podman tag aluna-api:latest christianbueno1/aluna-api:1.0.0

# Push
podman push christianbueno1/aluna-api:latest
podman push christianbueno1/aluna-api:1.0.0

# En otra máquina: pull
podman pull christianbueno1/aluna-api:latest
podman run -d -p 8000:8000 --env-file .env christianbueno1/aluna-api:latest
```

#### GitHub Container Registry
```bash
# Login con token personal
echo $GITHUB_TOKEN | podman login ghcr.io -u christianbueno1 --password-stdin

# Tag para GHCR
podman tag aluna-api:latest ghcr.io/christianbueno1/aluna-api:latest
podman tag aluna-api:latest ghcr.io/christianbueno1/aluna-api:1.0.0

# Push
podman push ghcr.io/christianbueno1/aluna-api:latest
podman push ghcr.io/christianbueno1/aluna-api:1.0.0

# Pull desde GHCR
podman pull ghcr.io/christianbueno1/aluna-api:latest
```

## 🐙 Docker Compose (alternativo)

```yaml
# docker-compose.yml o compose.yml
version: '3.8'

services:
  aluna-api:
    build:
      context: .
      dockerfile: Containerfile
    container_name: aluna-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  # Base de datos (opcional)
  postgres:
    image: postgres:17
    container_name: aluna-db
    environment:
      POSTGRES_USER: chris
      POSTGRES_PASSWORD: maGazine1!
      POSTGRES_DB: chris_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

```bash
# Usar con podman-compose
podman-compose up -d
podman-compose logs -f aluna-api
podman-compose down

# O con docker-compose
docker-compose up -d
docker-compose logs -f aluna-api
docker-compose down
```

## ⚙️ Variables de entorno importantes

```bash
# Crear archivo .env con estas variables mínimas
API_V1_PREFIX="/api/v1"
PROJECT_NAME="Aluna API"
MODELS_DIR="/app/modelos_entrenados"
DATABASE_URL="postgresql://chris:maGazine1!@localhost:5432/chris_db"

# Variables opcionales
DEBUG=false
LOG_LEVEL="info"
CORS_ORIGINS='["http://localhost:3000","https://miapp.com"]'
```

## 🚀 Quick Start para equipos nuevos

```bash
# 1. Clonar repositorio
git clone git@github.com:christianbueno1/aluna-api.git
cd aluna-api

# 2. Crear .env
cp .env.example .env
# Editar .env con tus credenciales de DB

# 3. Build y run (modelos ya incluidos)
podman build -t aluna-api:latest -f Containerfile .
podman run -d --name aluna-api -p 8000:8000 --env-file .env aluna-api:latest

# 4. Probar
curl http://localhost:8000/health
open http://localhost:8000/docs
```

## ⚠️ Notas importantes

1. **Modelos incluidos**: Los archivos `.joblib` están en la imagen (~18KB total)
   - No necesitas montar volúmenes
   - Todo self-contained para deployment simplificado
   - Para actualizar modelos: rebuild la imagen

2. **Versionado**: Usa tags semánticos para versionar código + modelos juntos
   ```bash
   podman build -t aluna-api:1.0.0 .
   podman build -t aluna-api:1.1.0 .  # Nueva versión con modelos actualizados
   ```

3. **Base de datos**: Si usas PostgreSQL externo:
   - Usar `--network` para conectar con contenedor de DB
   - O usar `host.containers.internal` para DB en host
   - O usar IP/hostname externo

4. **Puerto**: La app escucha en `0.0.0.0:8000` dentro del contenedor

5. **Usuario**: La app corre como usuario `aluna` (no-root) por seguridad

6. **Healthcheck**: Endpoint `/health` verifica que la API funciona correctamente

7. **Performance**: Multi-stage build mantiene imagen final ligera (~300-400MB)

8. **Python**: Usa Python 3.14.2 con Debian Trixie (latest stable)
