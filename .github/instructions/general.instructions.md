---
applyTo: '**'
---
# Plan de Desarrollo API - Modelos de Predicción Obstétrica

## 📋 Información de los Modelos

### Modelos Entrenados Disponibles

#### 1. Hemorragia Posparto - Decision Tree
- **Archivo**: `riesgo_hemorragia_posparto__DecisionTree.joblib`
- **Algoritmo**: Decision Tree Classifier
- **Propósito**: Predicción de riesgo de hemorragia posparto
- **Tipo**: Clasificación binaria o multiclase

#### 2. Hipertensión Gestacional - Decision Tree
- **Archivo**: `riesgo_hipertension_gestacional__DecisionTree.joblib`
- **Algoritmo**: Decision Tree Classifier
- **Propósito**: Predicción de riesgo de hipertensión gestacional
- **Tipo**: Clasificación binaria o multiclase

#### 3. Sepsis - Decision Tree
- **Archivo**: `riesgo_sepsis__DecisionTree.joblib`
- **Algoritmo**: Decision Tree Classifier
- **Propósito**: Predicción de riesgo de sepsis
- **Tipo**: Clasificación binaria o multiclase

---

## 🏗️ Plan de Desarrollo de la API

### Stack Tecnológico
- **Framework**: FastAPI
- **Validación**: Pydantic v2
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Serialización de Modelos**: Joblib
- **ML Libraries**: scikit-learn, lightgbm

## Datasets
```bash
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 5691 entries, 0 to 5690
Data columns (total 12 columns):
 #   Column                           Non-Null Count  Dtype  
---  ------                           --------------  -----  
 0   id_caso                          5691 non-null   int64  
 1   edad_materna                     5691 non-null   int64  
 2   paridad                          5691 non-null   int64  
 3   controles_prenatales             5691 non-null   int64  
 4   semanas_gestacion                5691 non-null   float64
 5   hipertension_previa              5691 non-null   int64  
 6   diabetes_gestacional             5691 non-null   int64  
 7   cesarea_previa                   5691 non-null   int64  
 8   embarazo_multiple                5691 non-null   int64  
 9   riesgo_sepsis                    5691 non-null   int64  
 10  riesgo_hipertension_gestacional  5691 non-null   int64  
 11  riesgo_hemorragia_posparto       5691 non-null   int64  
dtypes: float64(1), int64(11)
memory usage: 533.7 KB
Filas: 5691 | Features: 8
Targets: ['riesgo_sepsis', 'riesgo_hipertension_gestacional', 'riesgo_hemorragia_posparto']
```

# Model
Datos de entrada de un paciente obstétrico para predicción de riesgos.
id_caso                
edad_materna           
paridad                
controles_prenatales   
semanas_gestacion      
hipertension_previa    
diabetes_gestacional   
cesarea_previa         
embarazo_multiple

- Use schemes when defining models and endpoints.