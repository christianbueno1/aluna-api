"""
Punto de entrada principal de la API
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.events import startup_event, shutdown_event
from app.api.v1.router import router as api_v1_router


# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de contexto para eventos de ciclo de vida de la aplicación
    """
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Incluir routers
app.include_router(api_v1_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "API de Predicción de Complicaciones Obstétricas",
        "version": settings.API_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud
    """
    from app.services.ml_services import ModelLoader
    
    cached_models = ModelLoader.get_cached_models()
    
    return {
        "status": "healthy",
        "models_loaded": len(cached_models),
        "models": list(cached_models.keys())
    }


def main():
    """
    Función principal para ejecutar la aplicación
    """
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
