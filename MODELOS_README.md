# Modelos Entrenados - Proyecto Aluna API

Este archivo contiene los modelos de Machine Learning pre-entrenados para la predicción de riesgos obstétricos.

## 📦 Contenido

- `riesgo_sepsis__DecisionTree.joblib` + `.json`
- `riesgo_hipertension_gestacional__DecisionTree.joblib` + `.json`
- `riesgo_hemorragia_posparto__DecisionTree.joblib` + `.json`
- `manifest.json` - Metadata general de los modelos

## 🚀 Instalación

1. Descargar este archivo ZIP
2. Extraer en la raíz del proyecto `aluna-api`:
   ```bash
   cd aluna-api
   unzip modelos_entrenados.zip
   ```
3. Verificar que los archivos estén en su lugar:
   ```bash
   ls -lh modelos_entrenados/
   ```

## 📊 Información de los Modelos

- **Algoritmo**: Decision Tree Classifier
- **Features**: 8 variables obstétricas
- **Versión sklearn**: 1.6.1
- **Incluye**: StandardScaler pre-entrenado

## ⚠️ Nota

Estos archivos NO deben subirse al repositorio Git (están en `.gitignore`).
Comparte este ZIP directamente con los miembros del equipo.

## 🔗 Proyecto Generado Por

Grupo 6 - Entrenamiento_Proyecto_IA_Grupo_6.ipynb
