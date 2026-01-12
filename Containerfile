# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Builder
# ============================================
FROM docker.io/library/python:3.14.2-trixie AS builder

# Instalar uv para manejo de dependencias
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configurar variables de entorno para uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Directorio de trabajo temporal
WORKDIR /build

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias en directorio virtual
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ============================================
# Stage 2: Runtime
# ============================================
FROM docker.io/library/python:3.14.2-slim-trixie

# Metadata
LABEL maintainer="christianbueno1" \
      description="Aluna API - Sistema de predicción de riesgos obstétricos" \
      version="1.0.0" \
      python.version="3.14.2"

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r aluna && \
    useradd -r -g aluna -d /app -s /sbin/nologin aluna

# Directorio de trabajo
WORKDIR /app

# Copiar entorno virtual desde builder
COPY --from=builder --chown=aluna:aluna /build/.venv .venv

# Copiar archivos de la aplicación
COPY --chown=aluna:aluna app/ ./app/
COPY --chown=aluna:aluna alembic/ ./alembic/
COPY --chown=aluna:aluna alembic.ini ./
COPY --chown=aluna:aluna main.py ./

# Copiar modelos entrenados (self-contained image)
COPY --chown=aluna:aluna modelos_entrenados/ ./modelos_entrenados/

# Cambiar a usuario no-root
USER aluna

# Exponer puerto de la API
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto (producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
