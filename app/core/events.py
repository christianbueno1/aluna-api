"""
Eventos del ciclo de vida de la aplicación
"""
import logging
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings
from app.services.ml_services import ModelLoader, get_model_info


logger = logging.getLogger(__name__)


async def startup_event() -> None:
    """
    Evento de inicio de la aplicación.
    
    Realiza las siguientes tareas:
    1. Verifica el directorio de modelos
    2. Valida la existencia de archivos de modelos
    3. Pre-carga todos los modelos en memoria
    4. Registra información del sistema
    """
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO APLICACIÓN")
    logger.info("=" * 80)
    
    # 1. Verificar directorio de modelos
    logger.info("\n📁 VERIFICANDO DIRECTORIO DE MODELOS")
    logger.info("-" * 80)
    
    try:
        models_path = settings.models_path
        
        if not models_path.exists():
            logger.error(f"✗ El directorio de modelos NO existe: {models_path}")
            raise FileNotFoundError(f"Directorio de modelos no encontrado: {models_path}")
        
        logger.info(f"✓ Directorio de modelos encontrado: {models_path}")
        logger.info(f"  └─ Ruta absoluta: {models_path.resolve()}")
        
        # Listar archivos en el directorio
        model_files = list(models_path.glob("*.joblib"))
        logger.info(f"✓ Archivos .joblib encontrados: {len(model_files)}")
        for model_file in model_files:
            size_mb = model_file.stat().st_size / (1024 * 1024)
            logger.info(f"  └─ {model_file.name} ({size_mb:.2f} MB)")
        
    except Exception as e:
        logger.error(f"✗ Error al verificar directorio de modelos: {str(e)}")
        raise
    
    # 2. Validar archivos de modelos configurados
    logger.info("\n🔍 VALIDANDO ARCHIVOS DE MODELOS CONFIGURADOS")
    logger.info("-" * 80)
    
    try:
        models_info = get_model_info()
        
        for model_name, info in models_info.items():
            if info['exists']:
                logger.info(f"✓ Modelo '{model_name}':")
                logger.info(f"  ├─ Archivo: {Path(info['path']).name}")
                logger.info(f"  └─ Tamaño: {info['size_mb']} MB")
            else:
                logger.error(f"✗ Modelo '{model_name}' NO encontrado: {info['path']}")
                raise FileNotFoundError(f"Archivo de modelo no encontrado: {info['path']}")
        
        logger.info(f"✓ Todos los modelos configurados están presentes ({len(models_info)} modelos)")
        
    except Exception as e:
        logger.error(f"✗ Error al validar archivos de modelos: {str(e)}")
        raise
    
    # 3. Pre-carga de modelos en memoria
    logger.info("\n⚡ PRE-CARGA DE MODELOS EN MEMORIA")
    logger.info("-" * 80)
    
    try:
        # Cargar todos los modelos
        models = ModelLoader.load_all_models()
        
        logger.info(f"✓ Modelos cargados exitosamente en memoria:")
        for model_name, model in models.items():
            model_type = type(model).__name__
            logger.info(f"  └─ '{model_name}': {model_type}")
        
        # Verificar caché
        cached_models = ModelLoader.get_cached_models()
        logger.info(f"✓ Modelos en caché: {len(cached_models)}")
        
    except Exception as e:
        logger.error(f"✗ Error al pre-cargar modelos: {str(e)}")
        raise
    
    # 4. Información del sistema
    logger.info("\n📊 INFORMACIÓN DEL SISTEMA")
    logger.info("-" * 80)
    logger.info(f"API: {settings.API_TITLE}")
    logger.info(f"Versión: {settings.API_VERSION}")
    logger.info(f"Prefijo API: {settings.API_PREFIX}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Max Batch Size: {settings.MAX_BATCH_SIZE}")
    
    logger.info("\n🎯 UMBRALES DE CLASIFICACIÓN")
    logger.info("-" * 80)
    logger.info(f"Riesgo Alto: {settings.UMBRAL_RIESGO_ALTO}")
    logger.info(f"Riesgo Moderado: {settings.UMBRAL_RIESGO_MODERADO}")
    logger.info(f"Riesgo Bajo: {settings.UMBRAL_RIESGO_BAJO}")
    logger.info(f"Confianza Alta: {settings.UMBRAL_CONFIANZA_ALTA}")
    logger.info(f"Confianza Baja: {settings.UMBRAL_CONFIANZA_BAJA}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ APLICACIÓN INICIADA CORRECTAMENTE")
    logger.info("=" * 80 + "\n")


async def shutdown_event() -> None:
    """
    Evento de cierre de la aplicación.
    
    Realiza limpieza de recursos antes de cerrar.
    """
    logger.info("=" * 80)
    logger.info("🛑 CERRANDO APLICACIÓN")
    logger.info("=" * 80)
    
    # Limpiar caché de modelos
    logger.info("\n🧹 LIMPIANDO RECURSOS")
    logger.info("-" * 80)
    
    try:
        cached_models = ModelLoader.get_cached_models()
        logger.info(f"Limpiando {len(cached_models)} modelos del caché...")
        ModelLoader.clear_cache()
        logger.info("✓ Caché de modelos limpiado")
        
    except Exception as e:
        logger.error(f"✗ Error al limpiar recursos: {str(e)}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ APLICACIÓN CERRADA CORRECTAMENTE")
    logger.info("=" * 80 + "\n")


def get_startup_info() -> Dict[str, Any]:
    """
    Obtiene información del estado de inicio de la aplicación.
    
    Returns:
        Diccionario con información del sistema y modelos
    """
    return {
        "api": {
            "title": settings.API_TITLE,
            "version": settings.API_VERSION,
            "prefix": settings.API_PREFIX
        },
        "models": {
            "directory": str(settings.models_path),
            "models_info": get_model_info(),
            "cached_models": list(ModelLoader.get_cached_models().keys())
        },
        "config": {
            "max_batch_size": settings.MAX_BATCH_SIZE,
            "log_level": settings.LOG_LEVEL,
            "umbrales": {
                "riesgo_alto": settings.UMBRAL_RIESGO_ALTO,
                "riesgo_moderado": settings.UMBRAL_RIESGO_MODERADO,
                "riesgo_bajo": settings.UMBRAL_RIESGO_BAJO,
                "confianza_alta": settings.UMBRAL_CONFIANZA_ALTA,
                "confianza_baja": settings.UMBRAL_CONFIANZA_BAJA
            }
        }
    }
