# 1. Crear la estructura de directorios
mkdir -p app/{api/v1/endpoints,core,models,services,utils} tests modelos_entrenados

# 2. Crear los archivos __init__.py
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/api/v1/endpoints/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py

# 3. Copiar los archivos que te proporcioné en cada ubicación

# 4. Copiar modelos entrenados

## Opción A: Descargar modelos pre-empaquetados (Recomendado)
```bash
# 1. Descargar modelos_entrenados.zip desde Google Drive
# (Solicitar enlace al equipo o instructor)

# 2. Copiar el archivo zip a la raíz del proyecto
cp ~/Downloads/modelos_entrenados.zip .

# 3. Descomprimir
unzip modelos_entrenados.zip

# 4. Verificar que los archivos estén presentes
ls -lh modelos_entrenados/

# Deberías ver 7 archivos:
# - manifest.json
# - riesgo_sepsis__DecisionTree.joblib + .json
# - riesgo_hipertension_gestacional__DecisionTree.joblib + .json
# - riesgo_hemorragia_posparto__DecisionTree.joblib + .json
# - MODELOS_README.md
```

## Opción B: Generar modelos desde Google Colab
```bash
# 1. Ejecutar el notebook de entrenamiento en Google Colab
# 2. Descargar los archivos generados
# 3. Copiarlos a la carpeta modelos_entrenados/

# Archivos necesarios:
# - riesgo_sepsis__DecisionTree.joblib + .json
# - riesgo_hipertension_gestacional__DecisionTree.joblib + .json
# - riesgo_hemorragia_posparto__DecisionTree.joblib + .json
# - manifest.json

# Copiar desde tu ubicación de respaldo:
cp /ruta/a/tus/modelos/*.{joblib,json} modelos_entrenados/

# Verificar que estén presentes:
ls -lh modelos_entrenados/
```

## Para compartir modelos con el equipo
```bash
# Crear ZIP de los modelos (solo para administradores)
zip -r modelos_entrenados.zip modelos_entrenados/

# Agregar README de instrucciones al ZIP
zip modelos_entrenados.zip MODELOS_README.md

# Ver tamaño del archivo
ls -lh modelos_entrenados.zip

# Subir a Google Drive y compartir el enlace con el equipo
```

## ⚠️ Importante
Los archivos `.joblib` NO deben subirse al repositorio Git (están en `.gitignore`).
Comparte el ZIP directamente con los miembros del equipo.

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Configurar variables de entorno
cp .env.example .env

# 7. Ejecutar
python run.py --reload  # Desarrollo
python run.py --workers 4  # Producción

# Migraciones con Alembic

## Configuración inicial (ya completado ✓)
```bash
# 1. Inicializar Alembic en el proyecto
uv run alembic init alembic

# 2. Los archivos ya están configurados:
# - alembic.ini: Configuración comentada (se usa DATABASE_URL de .env)
# - alembic/env.py: Importa Base y settings automáticamente
# - app/core/config.py: Agregada variable DATABASE_URL
```

## Antes de crear migraciones

### 1. Iniciar base de datos con Podman
```bash
# El proyecto ya tiene un pod de PostgreSQL configurado
# Credenciales del pod (ver aluna-db-pod.yaml):
# - Usuario: chris
# - Base de datos: chris_db
# - Contraseña: maGazine1!
# - Puerto: 5434 (host) -> 5432 (container)

# Aplicar el pod con Podman
podman kube play aluna-db-pod.yaml

# Verificar que el pod está corriendo
podman pod ps
podman ps | grep aluna-db

# Ver logs del contenedor
podman logs aluna-db

# Detener el pod
podman kube down aluna-db-pod.yaml

# O detener directamente
podman pod stop aluna-db-pod
```

### 2. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo (ya tiene las credenciales correctas)
cp .env.example .env

# El .env ya contiene la configuración del pod:
# DATABASE_URL="postgresql://chris:maGazine1!@localhost:5434/chris_db"
# No necesitas modificarlo a menos que cambies las credenciales del pod
```

### 3. Alternativa: Base de datos local sin Podman
```bash
# Si prefieres PostgreSQL local en lugar del pod:

# Crear base de datos
psql -U postgres
CREATE DATABASE chris_db;
CREATE USER chris WITH PASSWORD 'maGazine1!';
GRANT ALL PRIVILEGES ON DATABASE chris_db TO chris;
\q

# Actualizar .env con puerto 5432 en lugar de 5434
# DATABASE_URL="postgresql://chris:maGazine1!@localhost:5432/chris_db"
```

## Crear y aplicar migraciones
```bash
# Crear migración inicial con los modelos obstétricos
uv run alembic revision --autogenerate -m "Create obstetric models"

# Aplicar todas las migraciones pendientes
uv run alembic upgrade head

# Ver el estado actual de las migraciones
uv run alembic current

# Ver historial de migraciones
uv run alembic history

# Revertir última migración
uv run alembic downgrade -1

# Revertir todas las migraciones
uv run alembic downgrade base
```

## Flujo de trabajo para cambios futuros
```bash
# 1. Modificar modelos en app/models/obstetric.py
# 2. Generar migración automática
uv run alembic revision --autogenerate -m "Descripción del cambio"

# 3. Revisar el archivo de migración generado en alembic/versions/
# 4. Aplicar la migración
uv run alembic upgrade head

# 5. Verificar que se aplicó correctamente
uv run alembic current
```

## Verificar tablas creadas
```bash
# Opción 1: Conectar al pod de Podman
podman exec -it aluna-db psql -U chris -d chris_db

# Opción 2: Conectar desde tu máquina (puerto 5434)
psql -U chris -d chris_db -h localhost -p 5434

# Ver las tablas creadas
\dt

# Deberías ver:
# - patient_cases
# - risk_predictions
# - alembic_version

# Ver estructura de una tabla
\d patient_cases
\d risk_predictions

# Salir
\q
```

# NOTES
```bash
cp .env.example .env

# Actualizar un paquete específico:
uv sync --upgrade-package pydantic-settings
# Actualizar todos los paquetes:
uv sync --upgrade
# O también puedes usar:
uv lock --upgrade-package pydantic-settings
uv sync

uv add scikit-learn==1.6.1
# si hay error instala
sudo dnf install gcc-c++

# 🧪 Prueba los Endpoints
# Endpoint raíz
curl http://127.0.0.1:8000/

# Health check
curl http://127.0.0.1:8000/health


# 🧪 Prueba los Endpoints
# Documentación interactiva
open http://127.0.0.1:8000/docs

# Predicción simple
curl -X POST http://127.0.0.1:8000/api/v1/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "edadMaterna": 35,
    "paridad": 2,
    "controlesPrenatales": 6,
    "semanasGestacion": 38.0,
    "hipertensionPrevia": 1,
    "diabetesGestacional": 0,
    "cesareaPrevia": 1,
    "embarazoMultiple": 0
  }' | jq