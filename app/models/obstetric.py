from sqlalchemy import String, Integer, Float, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from enum import IntEnum

class Base(DeclarativeBase):
    pass

# Define Enum for risk levels
class RiskLevel(IntEnum):
    """Niveles de riesgo para predicciones obstétricas"""
    BAJO = 0
    MEDIO = 1
    ALTO = 2

class PatientCase(Base):
    """
    Modelo para casos de pacientes obstétricas.
    Contiene los datos clínicos necesarios para las predicciones de riesgo.
    """
    __tablename__ = "patient_cases"
    
    # Primary key
    id_caso: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="Identificador único del caso")
    
    # Datos demográficos y clínicos
    edad_materna: Mapped[int] = mapped_column(Integer, nullable=False, comment="Edad de la madre en años")
    paridad: Mapped[int] = mapped_column(Integer, nullable=False, comment="Número de embarazos previos")
    controles_prenatales: Mapped[int] = mapped_column(Integer, nullable=False, comment="Número de controles prenatales realizados")
    semanas_gestacion: Mapped[float] = mapped_column(nullable=False, comment="Semanas de gestación (puede incluir decimales)")
    
    # Antecedentes médicos (valores booleanos: 0 o 1)
    hipertension_previa: Mapped[int] = mapped_column(Integer, default=0, comment="Historial de hipertensión (0: No, 1: Sí)")
    diabetes_gestacional: Mapped[int] = mapped_column(Integer, default=0, comment="Diagnóstico de diabetes gestacional (0: No, 1: Sí)")
    cesarea_previa: Mapped[int] = mapped_column(Integer, default=0, comment="Cesárea previa (0: No, 1: Sí)")
    embarazo_multiple: Mapped[int] = mapped_column(Integer, default=0, comment="Embarazo múltiple (0: No, 1: Sí)")
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.current_timestamp(),
        comment="Fecha de creación del registro"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.current_timestamp(), 
        server_default=func.current_timestamp(),
        comment="Fecha de última actualización"
    )
    
    # Relaciones
    predictions: Mapped[list["RiskPrediction"]] = relationship(
        back_populates="patient_case",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<PatientCase(id_caso={self.id_caso}, edad={self.edad_materna}, paridad={self.paridad}, semanas={self.semanas_gestacion})>"


class RiskPrediction(Base):
    """
    Modelo para almacenar las predicciones de riesgo obstétrico.
    Guarda los resultados de las predicciones de los tres modelos ML.
    """
    __tablename__ = "risk_predictions"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    
    # Foreign key al caso de paciente
    patient_case_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    
    # Predicciones de riesgo (0: Bajo, 1: Medio, 2: Alto)
    riesgo_sepsis: Mapped[int] = mapped_column(
        Integer, 
        nullable=True,
        comment="Predicción de riesgo de sepsis (0: Bajo, 1: Medio, 2: Alto)"
    )
    riesgo_hipertension_gestacional: Mapped[int] = mapped_column(
        Integer, 
        nullable=True,
        comment="Predicción de riesgo de hipertensión gestacional (0: Bajo, 1: Medio, 2: Alto)"
    )
    riesgo_hemorragia_posparto: Mapped[int] = mapped_column(
        Integer, 
        nullable=True,
        comment="Predicción de riesgo de hemorragia posparto (0: Bajo, 1: Medio, 2: Alto)"
    )
    
    # Probabilidades de predicción (opcional, si los modelos las proveen)
    probabilidad_sepsis: Mapped[float | None] = mapped_column(nullable=True)
    probabilidad_hipertension: Mapped[float | None] = mapped_column(nullable=True)
    probabilidad_hemorragia: Mapped[float | None] = mapped_column(nullable=True)
    
    # Metadata del modelo utilizado
    modelo_version: Mapped[str | None] = mapped_column(String, nullable=True, comment="Versión del modelo utilizado")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.current_timestamp(),
        comment="Fecha de la predicción"
    )
    
    # Relación con el caso de paciente
    patient_case: Mapped["PatientCase"] = relationship(back_populates="predictions")
    
    def __repr__(self):
        return f"<RiskPrediction(id={self.id}, id_caso={self.patient_case_id})>"
    
    def get_risk_summary(self) -> dict:
        """Retorna un resumen de los riesgos predichos"""
        return {
            "sepsis": {
                "nivel": self.riesgo_sepsis,
                "nivel_texto": self._get_risk_text(self.riesgo_sepsis),
                "probabilidad": self.probabilidad_sepsis
            },
            "hipertension_gestacional": {
                "nivel": self.riesgo_hipertension_gestacional,
                "nivel_texto": self._get_risk_text(self.riesgo_hipertension_gestacional),
                "probabilidad": self.probabilidad_hipertension
            },
            "hemorragia_posparto": {
                "nivel": self.riesgo_hemorragia_posparto,
                "nivel_texto": self._get_risk_text(self.riesgo_hemorragia_posparto),
                "probabilidad": self.probabilidad_hemorragia
            }
        }
    
    @staticmethod
    def _get_risk_text(risk_level: int | None) -> str:
        """Convierte el nivel de riesgo numérico a texto"""
        if risk_level is None:
            return "No evaluado"
        risk_map = {
            0: "Bajo",
            1: "Medio",
            2: "Alto"
        }
        return risk_map.get(risk_level, "Desconocido")
