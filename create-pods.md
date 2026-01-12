# Pods Creation using Podman
## PostgreSQL
```bash
# create a network
podman network create aluna-net && \
podman volume create aluna-db-data && \
podman volume create aluna-db-config
# create the pod for PostgreSQL
podman pod create --name aluna-db-pod --network aluna-net --publish 5434:5432 && \
# run the PostgreSQL container in the pod
podman run --pod aluna-db-pod \
  --name aluna-db \
  -e POSTGRES_DB=chris_db \
  -e POSTGRES_USER=chris \
  -e POSTGRES_PASSWORD=maGazine1! \
  -v aluna-db-data:/var/lib/postgresql/data \
  -v aluna-db-config:/etc/postgresql/conf.d \
  --restart=always \
  -d docker.io/library/postgres:16.10-trixie


# create the pod for the API
# image=docker.io/christianbueno1/aluna-api:latest
podman pod stop aluna-api-pod && podman pod rm aluna-api-pod && \
podman pod create --name aluna-api-pod --network aluna-net --publish 8002:8000 && \
# run the API container in the pod
podman run --pod aluna-api-pod \
  --name aluna-api \
  --env-file .env \
  --restart=always \
  -d docker.io/christianbueno1/aluna-api:latest

# stop, remove and run again
podman stop aluna-api && podman rm aluna-api && \
podman run --pod aluna-api-pod \
  --name aluna-api \
  --env-file .env \
  --restart=always \
  -d docker.io/christianbueno1/aluna-api:latest

podman logs aluna-api --tail 50
# remove pod
podman pod stop aluna-api-pod && podman pod rm aluna-api-pod

# en el servidor
# ALEMBIC MIGRATIONS
# Escenario 1: Primera vez en producción (base de datos vacía)
# 2. Ejecutar migraciones de Alembic dentro del contenedor
podman exec -it aluna-api alembic upgrade head

# Escenario 2: Base de datos existente (tu caso actual)
# Si ya tienes tablas creadas manualmente, necesitas sincronizar Alembic con el estado actual:
# 1. Generar el estado inicial de Alembic basado en la DB existente
podman exec -it aluna-api alembic revision --autogenerate -m "initial_schema"
# 2. Marcar como aplicada (sin ejecutar cambios)
podman exec -it aluna-api alembic stamp head

# Verificar si alembic existe
podman exec aluna-api which alembic
# Si existe, debería mostrar: /app/.venv/bin/alembic
podman exec aluna-api alembic --version
#
# 1. Ver estado actual de la base de datos
podman exec aluna-api alembic current
# 2. Aplicar todas las migraciones pendientes
podman exec aluna-api alembic upgrade head
# 3. Verificar que las tablas se crearon
podman exec aluna-db psql -U chris -d chris_db -c "\dt"
# 4. Ver estructura de las tablas
podman exec aluna-db psql -U chris -d chris_db -c "\d patient_cases"
podman exec aluna-db psql -U chris -d chris_db -c "\d risk_predictions"
# 5. Ver historial de migraciones aplicadas
podman exec aluna-api alembic history --verbose

# Esto confirma que las tablas ya están creadas. Verifica:
# Ver tablas existentes
podman exec aluna-db psql -U chris -d chris_db -c "\dt"
# Ver estructura de patient_cases
podman exec aluna-db psql -U chris -d chris_db -c "\d patient_cases"
# Ver estructura de risk_predictions
podman exec aluna-db psql -U chris -d chris_db -c "\d risk_predictions"
# Contar registros (debería ser 0 si es nueva)
podman exec aluna-db psql -U chris -d chris_db -c "SELECT COUNT(*) FROM patient_cases;"
podman exec aluna-db psql -U chris -d chris_db -c "SELECT COUNT(*) FROM risk_predictions;"