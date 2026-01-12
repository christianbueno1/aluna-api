"""
Servicio para carga y gestión de modelos de Machine Learning
"""
import joblib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

from app.core.config import settings


logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Clase para gestionar la carga y caché de modelos ML
    """
    _models_cache: Dict[str, Any] = {}
    
    @classmethod
    def load_model(cls, model_name: str) -> Any:
        """
        Carga un modelo específico desde el disco.
        
        Args:
            model_name: Nombre del modelo ('sepsis', 'hipertension_gestacional', 'hemorragia_posparto')
            
        Returns:
            El modelo cargado
            
        Raises:
            ValueError: Si el nombre del modelo no es válido
            FileNotFoundError: Si el archivo del modelo no existe
            Exception: Si hay un error al cargar el modelo
        """
        # Validar nombre del modelo
        valid_models = ['sepsis', 'hipertension_gestacional', 'hemorragia_posparto']
        if model_name not in valid_models:
            raise ValueError(
                f"Modelo '{model_name}' no válido. Modelos disponibles: {valid_models}"
            )
        
        # Verificar si el modelo ya está en caché
        if model_name in cls._models_cache:
            logger.info(f"✓ Modelo '{model_name}' cargado desde caché")
            return cls._models_cache[model_name]
        
        # Obtener la ruta del modelo
        model_path = settings.models_config.get(model_name)
        if not model_path:
            raise ValueError(f"No se encontró configuración para el modelo '{model_name}'")
        
        # Verificar que el archivo existe
        if not model_path.exists():
            raise FileNotFoundError(
                f"Archivo de modelo no encontrado: {model_path}"
            )
        
        try:
            # Cargar el modelo
            logger.info(f"Cargando modelo '{model_name}' desde {model_path}...")
            model_data = joblib.load(model_path)
            
            # Intentar cargar metadata JSON si existe
            json_path = model_path.with_suffix('.json')
            metadata = None
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                logger.info(f"✓ Metadata cargada para '{model_name}'")
            
            # Crear estructura unificada
            if isinstance(model_data, dict):
                # El modelo ya es un diccionario con 'model' y 'scaler'
                result = model_data
            else:
                # El modelo es solo el clasificador
                result = {'model': model_data, 'scaler': None}
            
            # Agregar metadata si existe
            if metadata:
                result['metadata'] = metadata
            
            # Guardar en caché
            cls._models_cache[model_name] = result
            
            logger.info(f"✓ Modelo '{model_name}' cargado exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"✗ Error al cargar modelo '{model_name}': {str(e)}")
            raise Exception(f"Error al cargar modelo '{model_name}': {str(e)}")
    
    @classmethod
    def load_all_models(cls) -> Dict[str, Any]:
        """
        Carga todos los modelos configurados.
        
        Returns:
            Diccionario con todos los modelos cargados
            
        Raises:
            Exception: Si hay un error al cargar algún modelo
        """
        models = {}
        model_names = ['sepsis', 'hipertension_gestacional', 'hemorragia_posparto']
        
        logger.info("Iniciando carga de todos los modelos...")
        
        for model_name in model_names:
            try:
                models[model_name] = cls.load_model(model_name)
            except Exception as e:
                logger.error(f"✗ Error al cargar modelo '{model_name}': {str(e)}")
                raise
        
        logger.info(f"✓ Todos los modelos cargados exitosamente ({len(models)} modelos)")
        return models
    
    @classmethod
    def get_model(cls, model_name: str) -> Any:
        """
        Obtiene un modelo del caché o lo carga si no está cacheado.
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            El modelo solicitado
        """
        if model_name not in cls._models_cache:
            return cls.load_model(model_name)
        return cls._models_cache[model_name]
    
    @classmethod
    def clear_cache(cls, model_name: Optional[str] = None) -> None:
        """
        Limpia el caché de modelos.
        
        Args:
            model_name: Nombre del modelo a limpiar. Si es None, limpia todo el caché.
        """
        if model_name:
            if model_name in cls._models_cache:
                del cls._models_cache[model_name]
                logger.info(f"Caché del modelo '{model_name}' limpiado")
        else:
            cls._models_cache.clear()
            logger.info("Caché de todos los modelos limpiado")
    
    @classmethod
    def get_cached_models(cls) -> Dict[str, Any]:
        """
        Retorna todos los modelos actualmente en caché.
        
        Returns:
            Diccionario con los modelos cacheados
        """
        return cls._models_cache.copy()
    
    @classmethod
    def is_model_cached(cls, model_name: str) -> bool:
        """
        Verifica si un modelo está en caché.
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            True si el modelo está en caché, False en caso contrario
        """
        return model_name in cls._models_cache


# Funciones de conveniencia para uso directo
def load_model(model_name: str) -> Any:
    """
    Carga un modelo específico.
    
    Args:
        model_name: Nombre del modelo ('sepsis', 'hipertension_gestacional', 'hemorragia_posparto')
        
    Returns:
        El modelo cargado
    """
    return ModelLoader.load_model(model_name)


def load_all_models() -> Dict[str, Any]:
    """
    Carga todos los modelos configurados.
    
    Returns:
        Diccionario con todos los modelos cargados
    """
    return ModelLoader.load_all_models()


def get_model(model_name: str) -> Any:
    """
    Obtiene un modelo del caché o lo carga si no está cacheado.
    
    Args:
        model_name: Nombre del modelo
        
    Returns:
        El modelo solicitado
    """
    return ModelLoader.get_model(model_name)


def get_model_info() -> Dict[str, Dict[str, Any]]:
    """
    Obtiene información sobre los modelos configurados.
    
    Returns:
        Diccionario con información de cada modelo
    """
    info = {}
    
    for model_name, model_path in settings.models_config.items():
        info[model_name] = {
            'path': str(model_path),
            'exists': model_path.exists(),
            'cached': ModelLoader.is_model_cached(model_name),
            'size_mb': round(model_path.stat().st_size / (1024 * 1024), 2) if model_path.exists() else None
        }
    
    return info
