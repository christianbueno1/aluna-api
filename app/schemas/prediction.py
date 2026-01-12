"""
Schemas para predicciones de riesgos obstétricos
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List
from enum import Enum


class RiskLevel(str, Enum):
    """Niveles de riesgo"""
    ALTO = "alto"
    MODERADO = "moderado"
    BAJO = "bajo"
    MUY_BAJO = "muy_bajo"


class ConfidenceLevel(str, Enum):
    """Niveles de confianza"""
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class PatientData(BaseModel):
    """
    Datos de entrada de un paciente obstétrico para predicción de riesgos
    """
    edad_materna: int = Field(..., ge=15, le=60, description="Edad de la madre en años (15-60)")
    paridad: int = Field(..., ge=0, le=20, description="Número de partos previos (0-20)")
    controles_prenatales: int = Field(..., ge=0, le=20, description="Número de controles prenatales realizados (0-20)")
    semanas_gestacion: float = Field(..., ge=4.0, le=45.0, description="Semanas de gestación (4.0-45.0)")
    hipertension_previa: int = Field(..., ge=0, le=1, description="Hipertensión previa (0=No, 1=Sí)")
    diabetes_gestacional: int = Field(..., ge=0, le=1, description="Diabetes gestacional (0=No, 1=Sí)")
    cesarea_previa: int = Field(..., ge=0, le=1, description="Cesárea previa (0=No, 1=Sí)")
    embarazo_multiple: int = Field(..., ge=0, le=1, description="Embarazo múltiple (0=No, 1=Sí)")
    
    @field_validator('hipertension_previa', 'diabetes_gestacional', 'cesarea_previa', 'embarazo_multiple')
    @classmethod
    def validate_binary(cls, v: int) -> int:
        if v not in [0, 1]:
            raise ValueError('El valor debe ser 0 o 1')
        return v
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )


class RiskPrediction(BaseModel):
    """Predicción de riesgo individual"""
    riesgo: str = Field(..., description="Tipo de riesgo")
    probabilidad: float = Field(..., ge=0.0, le=1.0, description="Probabilidad del riesgo (0.0-1.0)")
    nivel_riesgo: RiskLevel = Field(..., description="Nivel de riesgo clasificado")
    nivel_confianza: ConfidenceLevel = Field(..., description="Nivel de confianza de la predicción")
    recomendacion: str = Field(..., description="Recomendación basada en el nivel de riesgo")
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )


class PredictionResponse(BaseModel):
    """Respuesta de predicción completa para un paciente"""
    predicciones: List[RiskPrediction] = Field(..., description="Lista de predicciones de riesgos")
    resumen: dict = Field(..., description="Resumen general de los riesgos")
    datos_paciente: PatientData = Field(..., description="Datos del paciente utilizados")
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )


class BatchPredictionRequest(BaseModel):
    """Petición de predicción por lotes"""
    pacientes: List[PatientData] = Field(..., max_length=100, description="Lista de pacientes (máximo 100)")
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )


class BatchPredictionResponse(BaseModel):
    """Respuesta de predicción por lotes"""
    total_pacientes: int = Field(..., description="Total de pacientes procesados")
    predicciones: List[PredictionResponse] = Field(..., description="Lista de predicciones")
    estadisticas: dict = Field(..., description="Estadísticas del lote procesado")
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )
