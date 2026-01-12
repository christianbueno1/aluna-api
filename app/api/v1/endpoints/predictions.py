"""
Endpoints para predicciones de riesgos obstétricos
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.prediction import (
    PatientData,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse
)
from app.services.prediction_service import PredictionService
from app.core.config import settings


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predicción de riesgos para un paciente",
    description="Realiza predicción de los 3 riesgos obstétricos (sepsis, hipertensión gestacional, hemorragia posparto) para un paciente",
    response_description="Predicciones de riesgos con niveles y recomendaciones"
)
async def predict_patient(patient_data: PatientData) -> PredictionResponse:
    """
    Predice los riesgos obstétricos para un paciente.
    
    **Parámetros:**
    - **edad_materna**: Edad de la madre (15-60 años)
    - **paridad**: Número de partos previos (0-20)
    - **controles_prenatales**: Número de controles realizados (0-20)
    - **semanas_gestacion**: Semanas de gestación (4.0-45.0)
    - **hipertension_previa**: Hipertensión previa (0=No, 1=Sí)
    - **diabetes_gestacional**: Diabetes gestacional (0=No, 1=Sí)
    - **cesarea_previa**: Cesárea previa (0=No, 1=Sí)
    - **embarazo_multiple**: Embarazo múltiple (0=No, 1=Sí)
    
    **Retorna:**
    - Predicciones para los 3 riesgos con probabilidades, niveles y recomendaciones
    - Resumen general del estado del paciente
    """
    try:
        logger.info(f"Recibida petición de predicción: edad={patient_data.edad_materna}, semanas={patient_data.semanas_gestacion}")
        
        result = PredictionService.predict_all_risks(patient_data)
        
        logger.info(f"Predicción exitosa: riesgo_general={result.resumen['riesgo_general']}")
        return result
        
    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar predicción: {str(e)}"
        )


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predicción por lotes",
    description=f"Realiza predicciones para múltiples pacientes (máximo {settings.MAX_BATCH_SIZE})",
    response_description="Predicciones para todos los pacientes con estadísticas generales"
)
async def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """
    Realiza predicciones para múltiples pacientes en un solo request.
    
    **Límites:**
    - Máximo de pacientes por lote: {max_batch_size}
    
    **Retorna:**
    - Predicciones individuales para cada paciente
    - Estadísticas agregadas del lote
    """
    try:
        num_patients = len(request.pacientes)
        logger.info(f"Recibida petición de lote con {num_patients} pacientes")
        
        if num_patients > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Número de pacientes ({num_patients}) excede el límite máximo ({settings.MAX_BATCH_SIZE})"
            )
        
        # Realizar predicciones para cada paciente
        predictions = []
        for i, patient_data in enumerate(request.pacientes):
            try:
                result = PredictionService.predict_all_risks(patient_data)
                predictions.append(result)
            except Exception as e:
                logger.error(f"Error al predecir paciente {i+1}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al procesar paciente {i+1}: {str(e)}"
                )
        
        # Calcular estadísticas del lote
        stats = _calculate_batch_statistics(predictions)
        
        logger.info(f"Lote procesado exitosamente: {num_patients} pacientes")
        
        return BatchPredictionResponse(
            total_pacientes=num_patients,
            predicciones=predictions,
            estadisticas=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en predicción por lote: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar predicción por lote: {str(e)}"
        )


@router.post(
    "/predict/risk/{risk_type}",
    status_code=status.HTTP_200_OK,
    summary="Predicción de un riesgo específico",
    description="Realiza predicción para un tipo de riesgo específico",
    response_description="Predicción del riesgo solicitado"
)
async def predict_single_risk(risk_type: str, patient_data: PatientData):
    """
    Predice un riesgo específico para un paciente.
    
    **Tipos de riesgo disponibles:**
    - `sepsis`: Riesgo de sepsis
    - `hipertension_gestacional`: Riesgo de hipertensión gestacional
    - `hemorragia_posparto`: Riesgo de hemorragia posparto
    """
    try:
        valid_risks = ['sepsis', 'hipertension_gestacional', 'hemorragia_posparto']
        
        if risk_type not in valid_risks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de riesgo '{risk_type}' no válido. Tipos disponibles: {valid_risks}"
            )
        
        logger.info(f"Predicción de riesgo específico: {risk_type}")
        
        prediction = PredictionService.predict_single_risk(patient_data, risk_type)
        
        return {
            "prediccion": prediction.model_dump(by_alias=True),
            "datos_paciente": patient_data.model_dump(by_alias=True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en predicción de {risk_type}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar predicción: {str(e)}"
        )


def _calculate_batch_statistics(predictions: List[PredictionResponse]) -> dict:
    """
    Calcula estadísticas agregadas de un lote de predicciones
    
    Args:
        predictions: Lista de predicciones
        
    Returns:
        Diccionario con estadísticas
    """
    total = len(predictions)
    
    # Contadores por nivel de riesgo general
    risk_distribution = {
        'alto': 0,
        'moderado': 0,
        'bajo': 0,
        'muy_bajo': 0
    }
    
    # Contadores por tipo de riesgo
    risk_type_high = {
        'sepsis': 0,
        'hipertension_gestacional': 0,
        'hemorragia_posparto': 0
    }
    
    require_special_attention = 0
    
    for pred_response in predictions:
        # Distribución de riesgo general
        general_risk = pred_response.resumen.get('riesgo_general', 'bajo')
        risk_distribution[general_risk] += 1
        
        # Atención especial
        if pred_response.resumen.get('requiere_atencion_especial', False):
            require_special_attention += 1
        
        # Riesgos altos por tipo
        for prediction in pred_response.predicciones:
            if prediction.nivel_riesgo.value == 'alto':
                risk_type_high[prediction.riesgo] += 1
    
    return {
        'total_procesados': total,
        'distribucion_riesgo_general': risk_distribution,
        'pacientes_atencion_especial': require_special_attention,
        'porcentaje_atencion_especial': round((require_special_attention / total * 100), 2) if total > 0 else 0,
        'riesgos_altos_por_tipo': risk_type_high,
        'promedios': {
            'alto': round((risk_distribution['alto'] / total * 100), 2) if total > 0 else 0,
            'moderado': round((risk_distribution['moderado'] / total * 100), 2) if total > 0 else 0,
            'bajo': round((risk_distribution['bajo'] / total * 100), 2) if total > 0 else 0
        }
    }
