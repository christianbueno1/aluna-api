"""
Servicio de predicción de riesgos obstétricos
"""
import numpy as np
import logging
from typing import Dict, List, Tuple

from app.schemas.prediction import (
    PatientData,
    RiskPrediction,
    PredictionResponse,
    RiskLevel,
    ConfidenceLevel
)
from app.services.ml_services import get_model
from app.core.config import settings


logger = logging.getLogger(__name__)


class PredictionService:
    """
    Servicio para realizar predicciones de riesgos obstétricos
    """
    
    # Nombres de features en el orden correcto para los modelos
    FEATURE_NAMES = [
        'edad_materna',
        'paridad',
        'controles_prenatales',
        'semanas_gestacion',
        'hipertension_previa',
        'diabetes_gestacional',
        'cesarea_previa',
        'embarazo_multiple'
    ]
    
    # Configuración de riesgos
    RISK_TYPES = {
        'sepsis': 'Sepsis',
        'hipertension_gestacional': 'Hipertensión Gestacional',
        'hemorragia_posparto': 'Hemorragia Posparto'
    }
    
    @staticmethod
    def prepare_features(patient_data: PatientData) -> np.ndarray:
        """
        Prepara las features del paciente en el formato correcto para el modelo
        
        Args:
            patient_data: Datos del paciente
            
        Returns:
            Array numpy con las features en el orden correcto
        """
        features = np.array([[
            patient_data.edad_materna,
            patient_data.paridad,
            patient_data.controles_prenatales,
            patient_data.semanas_gestacion,
            patient_data.hipertension_previa,
            patient_data.diabetes_gestacional,
            patient_data.cesarea_previa,
            patient_data.embarazo_multiple
        ]])
        
        return features
    
    @staticmethod
    def classify_risk_level(probability: float) -> RiskLevel:
        """
        Clasifica el nivel de riesgo según la probabilidad y umbrales configurados
        
        Args:
            probability: Probabilidad del riesgo (0.0-1.0)
            
        Returns:
            Nivel de riesgo clasificado
        """
        if probability >= settings.UMBRAL_RIESGO_ALTO:
            return RiskLevel.ALTO
        elif probability >= settings.UMBRAL_RIESGO_MODERADO:
            return RiskLevel.MODERADO
        elif probability >= settings.UMBRAL_RIESGO_BAJO:
            return RiskLevel.BAJO
        else:
            return RiskLevel.MUY_BAJO
    
    @staticmethod
    def classify_confidence_level(probability: float, model_type: str = 'DecisionTree') -> ConfidenceLevel:
        """
        Clasifica el nivel de confianza de la predicción
        
        Args:
            probability: Probabilidad predicha
            model_type: Tipo de modelo utilizado
            
        Returns:
            Nivel de confianza
        """
        # Para decisiones extremas (muy cerca de 0 o 1), mayor confianza
        if probability >= settings.UMBRAL_CONFIANZA_ALTA or probability <= (1 - settings.UMBRAL_CONFIANZA_ALTA):
            return ConfidenceLevel.ALTA
        elif probability >= settings.UMBRAL_CONFIANZA_BAJA or probability <= (1 - settings.UMBRAL_CONFIANZA_BAJA):
            return ConfidenceLevel.MEDIA
        else:
            return ConfidenceLevel.BAJA
    
    @staticmethod
    def generate_recommendation(risk_type: str, risk_level: RiskLevel) -> str:
        """
        Genera recomendación basada en el tipo y nivel de riesgo
        
        Args:
            risk_type: Tipo de riesgo
            risk_level: Nivel de riesgo
            
        Returns:
            Recomendación médica
        """
        recommendations = {
            'sepsis': {
                RiskLevel.ALTO: 'URGENTE: Evaluación inmediata. Monitoreo intensivo de signos vitales y marcadores de infección. Considerar antibióticos profilácticos.',
                RiskLevel.MODERADO: 'Vigilancia estrecha de signos de infección. Control de temperatura cada 4 horas. Educación sobre signos de alarma.',
                RiskLevel.BAJO: 'Seguimiento estándar. Higiene adecuada. Educación sobre signos de infección.',
                RiskLevel.MUY_BAJO: 'Seguimiento rutinario prenatal. Medidas preventivas estándar.'
            },
            'hipertension_gestacional': {
                RiskLevel.ALTO: 'URGENTE: Monitoreo continuo de presión arterial. Evaluación de preeclampsia. Posible hospitalización. Control de proteínas en orina.',
                RiskLevel.MODERADO: 'Monitoreo frecuente de presión arterial (cada 2-3 días). Control de edemas. Restricción de sal. Educación sobre signos de alarma.',
                RiskLevel.BAJO: 'Control prenatal regular con monitoreo de presión arterial. Dieta balanceada baja en sodio.',
                RiskLevel.MUY_BAJO: 'Seguimiento prenatal estándar. Mantener estilo de vida saludable.'
            },
            'hemorragia_posparto': {
                RiskLevel.ALTO: 'URGENTE: Preparación para parto en centro con banco de sangre. Disponibilidad de uterotónicos. Equipo quirúrgico en alerta.',
                RiskLevel.MODERADO: 'Parto en centro hospitalario. Preparación de sangre disponible. Vigilancia estrecha del alumbramiento y posparto inmediato.',
                RiskLevel.BAJO: 'Seguimiento estándar. Asegurar manejo activo del alumbramiento. Vigilancia posparto.',
                RiskLevel.MUY_BAJO: 'Seguimiento prenatal rutinario. Parto con manejo activo del alumbramiento.'
            }
        }
        
        return recommendations.get(risk_type, {}).get(
            risk_level,
            'Seguimiento según protocolo médico estándar'
        )
    
    @classmethod
    def predict_single_risk(cls, patient_data: PatientData, risk_type: str) -> RiskPrediction:
        """
        Realiza predicción para un tipo de riesgo específico
        
        Args:
            patient_data: Datos del paciente
            risk_type: Tipo de riesgo a predecir
            
        Returns:
            Predicción del riesgo
        """
        # Obtener el modelo
        model_dict = get_model(risk_type)
        model = model_dict.get('model_obj') or model_dict.get('model')
        scaler = model_dict.get('scaler')
        
        # Preparar features
        features = cls.prepare_features(patient_data)
        
        # Escalar si existe scaler
        if scaler:
            features = scaler.transform(features)
        
        # Realizar predicción
        probability = model.predict_proba(features)[0][1]  # Probabilidad de la clase positiva
        
        # Clasificar nivel de riesgo
        risk_level = cls.classify_risk_level(probability)
        
        # Clasificar confianza
        confidence_level = cls.classify_confidence_level(probability)
        
        # Generar recomendación
        recommendation = cls.generate_recommendation(risk_type, risk_level)
        
        logger.info(f"Predicción {risk_type}: probabilidad={probability:.4f}, nivel={risk_level.value}")
        
        return RiskPrediction(
            riesgo=risk_type,
            probabilidad=round(float(probability), 4),
            nivel_riesgo=risk_level,
            nivel_confianza=confidence_level,
            recomendacion=recommendation
        )
    
    @classmethod
    def predict_all_risks(cls, patient_data: PatientData) -> PredictionResponse:
        """
        Realiza predicción para todos los tipos de riesgo
        
        Args:
            patient_data: Datos del paciente
            
        Returns:
            Respuesta completa con todas las predicciones
        """
        logger.info(f"Iniciando predicción para paciente: edad={patient_data.edad_materna}, semanas={patient_data.semanas_gestacion}")
        
        # Realizar predicciones para cada tipo de riesgo
        predictions = []
        for risk_type in cls.RISK_TYPES.keys():
            try:
                prediction = cls.predict_single_risk(patient_data, risk_type)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error al predecir {risk_type}: {str(e)}")
                raise
        
        # Generar resumen
        summary = cls.generate_summary(predictions)
        
        logger.info(f"Predicción completada: {summary}")
        
        return PredictionResponse(
            predicciones=predictions,
            resumen=summary,
            datos_paciente=patient_data
        )
    
    @staticmethod
    def generate_summary(predictions: List[RiskPrediction]) -> Dict:
        """
        Genera resumen general de las predicciones
        
        Args:
            predictions: Lista de predicciones
            
        Returns:
            Diccionario con resumen
        """
        # Contar riesgos por nivel
        risk_counts = {
            'alto': 0,
            'moderado': 0,
            'bajo': 0,
            'muy_bajo': 0
        }
        
        max_probability = 0.0
        max_risk = None
        
        for pred in predictions:
            risk_counts[pred.nivel_riesgo.value] += 1
            if pred.probabilidad > max_probability:
                max_probability = pred.probabilidad
                max_risk = pred.riesgo
        
        # Determinar riesgo general
        if risk_counts['alto'] > 0:
            general_risk = 'alto'
        elif risk_counts['moderado'] > 0:
            general_risk = 'moderado'
        elif risk_counts['bajo'] > 0:
            general_risk = 'bajo'
        else:
            general_risk = 'muy_bajo'
        
        return {
            'riesgo_general': general_risk,
            'total_riesgos_altos': risk_counts['alto'],
            'total_riesgos_moderados': risk_counts['moderado'],
            'total_riesgos_bajos': risk_counts['bajo'],
            'requiere_atencion_especial': risk_counts['alto'] > 0 or risk_counts['moderado'] >= 2,
            'riesgo_mas_alto': max_risk,
            'probabilidad_mas_alta': round(max_probability, 4)
        }


# Función de conveniencia
def predict_patient_risks(patient_data: PatientData) -> PredictionResponse:
    """
    Función de conveniencia para realizar predicción completa
    
    Args:
        patient_data: Datos del paciente
        
    Returns:
        Respuesta con todas las predicciones
    """
    return PredictionService.predict_all_risks(patient_data)
