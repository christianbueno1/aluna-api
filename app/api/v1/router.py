"""
Router principal de la API v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import predictions


router = APIRouter()

# Incluir routers de endpoints
router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["Predicciones"]
)
