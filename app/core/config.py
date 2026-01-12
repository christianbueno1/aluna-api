"""
Configuración central de la aplicación
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from pathlib import Path
from typing import List, Dict
import logging


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando variables de entorno
    """
    # Información de la API
    API_TITLE: str = "Sistema de Predicción de Complicaciones Obstétricas"
    API_DESCRIPTION: str = "API para predecir riesgo de sepsis, hipertensión gestacional y hemorragia posparto"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # En producción, especificar dominios permitidos
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Rutas base
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODELS_DIR: str = "modelos_entrenados"  # Ruta relativa o absoluta
    
    # Base de datos (configuración del pod aluna-db-pod)
    DATABASE_URL: str = "postgresql://chris:maGazine1!@localhost:5434/chris_db"
    
    # Nombres de archivos de modelos
    MODEL_SEPSIS: str = "riesgo_sepsis__DecisionTree.joblib"
    MODEL_HIPERTENSION_GESTACIONAL: str = "riesgo_hipertension_gestacional__DecisionTree.joblib"
    MODEL_HEMORRAGIA_POSPARTO: str = "riesgo_hemorragia_posparto__DecisionTree.joblib"
    
    # Límites
    MAX_BATCH_SIZE: int = 100
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    
    # Umbrales de clasificación
    UMBRAL_RIESGO_ALTO: float = 0.7
    UMBRAL_RIESGO_MODERADO: float = 0.5
    UMBRAL_RIESGO_BAJO: float = 0.3
    
    UMBRAL_CONFIANZA_ALTA: float = 0.8
    UMBRAL_CONFIANZA_BAJA: float = 0.6
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    @field_validator('MODELS_DIR')
    @classmethod
    def validate_models_dir(cls, v: str, info) -> str:
        """
        Valida que el directorio de modelos existe
        """
        # Obtener BASE_DIR del contexto
        base_dir = Path(__file__).resolve().parent.parent.parent
        
        # Construir la ruta completa
        models_path = Path(v) if Path(v).is_absolute() else base_dir / v
        
        # Verificar que existe
        if not models_path.exists():
            raise ValueError(f"El directorio de modelos no existe: {models_path}")
        
        if not models_path.is_dir():
            raise ValueError(f"La ruta de modelos no es un directorio: {models_path}")
        
        logger.info(f"✓ Directorio de modelos validado: {models_path}")
        return str(v)
    
    @model_validator(mode='after')
    def validate_model_files(self) -> 'Settings':
        """
        Valida que todos los archivos de modelos existen
        """
        models_path = Path(self.MODELS_DIR) if Path(self.MODELS_DIR).is_absolute() else self.BASE_DIR / self.MODELS_DIR
        
        model_files = {
            'sepsis': self.MODEL_SEPSIS,
            'hipertension_gestacional': self.MODEL_HIPERTENSION_GESTACIONAL,
            'hemorragia_posparto': self.MODEL_HEMORRAGIA_POSPARTO
        }
        
        missing_files = []
        for name, filename in model_files.items():
            model_path = models_path / filename
            if not model_path.exists():
                missing_files.append(f"{name}: {filename}")
            else:
                logger.info(f"✓ Modelo encontrado: {name} -> {model_path}")
        
        if missing_files:
            raise ValueError(f"Archivos de modelo faltantes:\n" + "\n".join(f"  - {f}" for f in missing_files))
        
        return self
    
    @property
    def models_path(self) -> Path:
        """
        Retorna la ruta completa al directorio de modelos
        """
        models_dir = Path(self.MODELS_DIR) if Path(self.MODELS_DIR).is_absolute() else self.BASE_DIR / self.MODELS_DIR
        return models_dir.resolve()
    
    @property
    def models_config(self) -> Dict[str, Path]:
        """
        Retorna un diccionario con las rutas completas de cada modelo
        """
        return {
            'sepsis': self.models_path / self.MODEL_SEPSIS,
            'hipertension_gestacional': self.models_path / self.MODEL_HIPERTENSION_GESTACIONAL,
            'hemorragia_posparto': self.models_path / self.MODEL_HEMORRAGIA_POSPARTO
        }


# Instancia global de settings
settings = Settings()