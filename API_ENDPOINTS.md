# 🏥 Aluna API - Guía para Frontend

## 📋 Información General

**URL Base Producción:** `https://aluna-api.deployhero.dev`  
**URL Base Local:** `http://localhost:8002`

**Versión:** 1.0.0  
**Formato:** JSON  
**Charset:** UTF-8 (soporta caracteres especiales en español)

---

## 🔗 Endpoints Disponibles

### 1. Health Check

Verificar estado de la API y modelos cargados.

**Endpoint:** `GET /health`

**Respuesta Exitosa (200):**
```json
{
  "status": "healthy",
  "models_loaded": 3,
  "models": [
    "sepsis",
    "hipertension_gestacional",
    "hemorragia_posparto"
  ]
}
```

**Ejemplo curl:**
```bash
curl https://aluna-api.deployhero.dev/health
```

---

### 2. Documentación Interactiva

**Swagger UI:** `GET /docs`  
**ReDoc:** `GET /redoc`

Abrir en navegador:
- https://aluna-api.deployhero.dev/docs
- https://aluna-api.deployhero.dev/redoc

---

### 3. Predicción de Riesgos (Individual)

Predecir riesgos obstétricos para un solo paciente.

**Endpoint:** `POST /api/v1/predictions/predict`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "edadMaterna": 35,
  "paridad": 2,
  "controlesPrenatales": 6,
  "semanasGestacion": 38.0,
  "hipertensionPrevia": 1,
  "diabetesGestacional": 0,
  "cesareaPrevia": 1,
  "embarazoMultiple": 0
}
```

**Campos (todos requeridos):**

| Campo | Tipo | Descripción | Rango |
|-------|------|-------------|-------|
| `edadMaterna` | integer | Edad de la madre en años | 15-60 |
| `paridad` | integer | Número de partos previos | 0-20 |
| `controlesPrenatales` | integer | Cantidad de controles prenatales | 0-20 |
| `semanasGestacion` | float | Semanas de gestación | 4.0-45.0 |
| `hipertensionPrevia` | integer | Hipertensión previa (0=No, 1=Sí) | 0 o 1 |
| `diabetesGestacional` | integer | Diabetes gestacional (0=No, 1=Sí) | 0 o 1 |
| `cesareaPrevia` | integer | Cesárea previa (0=No, 1=Sí) | 0 o 1 |
| `embarazoMultiple` | integer | Embarazo múltiple (0=No, 1=Sí) | 0 o 1 |

**Respuesta Exitosa (200):**
```json
{
  "predicciones": [
    {
      "riesgo": "sepsis",
      "probabilidad": 0.2675,
      "nivelRiesgo": "muy_bajo",
      "nivelConfianza": "media",
      "recomendacion": "Seguimiento rutinario prenatal. Medidas preventivas estándar."
    },
    {
      "riesgo": "hipertension_gestacional",
      "probabilidad": 0.7386,
      "nivelRiesgo": "alto",
      "nivelConfianza": "media",
      "recomendacion": "URGENTE: Monitoreo continuo de presión arterial. Evaluación de preeclampsia. Posible hospitalización. Control de proteínas en orina."
    },
    {
      "riesgo": "hemorragia_posparto",
      "probabilidad": 0.5908,
      "nivelRiesgo": "moderado",
      "nivelConfianza": "baja",
      "recomendacion": "Parto en centro hospitalario. Preparación de sangre disponible. Vigilancia estrecha del alumbramiento y posparto inmediato."
    }
  ],
  "resumen": {
    "riesgo_general": "alto",
    "total_riesgos_altos": 1,
    "total_riesgos_moderados": 1,
    "total_riesgos_bajos": 0,
    "requiere_atencion_especial": true,
    "riesgo_mas_alto": "hipertension_gestacional",
    "probabilidad_mas_alta": 0.7386
  },
  "datosPaciente": {
    "edadMaterna": 35,
    "paridad": 2,
    "controlesPrenatales": 6,
    "semanasGestacion": 38.0,
    "hipertensionPrevia": 1,
    "diabetesGestacional": 0,
    "cesareaPrevia": 1,
    "embarazoMultiple": 0
  }
}
```

**Niveles de Riesgo:**
- `muy_bajo`: Probabilidad < 30%
- `bajo`: Probabilidad ≥ 30% y < 50%
- `moderado`: Probabilidad ≥ 50% y < 70%
- `alto`: Probabilidad ≥ 70%

**Niveles de Confianza:**
- `alta`: Probabilidad ≥ 80%
- `media`: Probabilidad ≥ 60% y < 80%
- `baja`: Probabilidad < 60%

**Ejemplo curl:**
```bash
curl -X POST https://aluna-api.deployhero.dev/api/v1/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "edadMaterna": 35,
    "paridad": 2,
    "controlesPrenatales": 6,
    "semanasGestacion": 38.0,
    "hipertensionPrevia": 1,
    "diabetesGestacional": 0,
    "cesareaPrevia": 1,
    "embarazoMultiple": 0
  }'
```

**Ejemplo JavaScript (Fetch):**
```javascript
async function predecirRiesgos(datosPaciente) {
  const response = await fetch('https://aluna-api.deployhero.dev/api/v1/predictions/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datosPaciente)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// Uso
const resultado = await predecirRiesgos({
  edadMaterna: 35,
  paridad: 2,
  controlesPrenatales: 6,
  semanasGestacion: 38.0,
  hipertensionPrevia: 1,
  diabetesGestacional: 0,
  cesareaPrevia: 1,
  embarazoMultiple: 0
});

console.log(resultado.resumen.riesgo_general); // "alto"
console.log(resultado.predicciones[0].recomendacion);
```

**Ejemplo JavaScript (Axios):**
```javascript
import axios from 'axios';

const predecirRiesgos = async (datosPaciente) => {
  try {
    const { data } = await axios.post(
      'https://aluna-api.deployhero.dev/api/v1/predictions/predict',
      datosPaciente
    );
    return data;
  } catch (error) {
    console.error('Error en predicción:', error.response?.data);
    throw error;
  }
};
```

**Errores Comunes:**

**422 - Validation Error:**
```json
{
  "detail": [
    {
      "type": "int_type",
      "loc": ["body", "edadMaterna"],
      "msg": "Input should be a valid integer",
      "input": "treinta y cinco"
    }
  ]
}
```

---

### 4. Predicción por Lotes (Batch)

Predecir riesgos para múltiples pacientes en una sola petición.

**Endpoint:** `POST /api/v1/predictions/batch`

**Límite:** Máximo 100 pacientes por petición

**Body (JSON):**
```json
{
  "pacientes": [
    {
      "edadMaterna": 28,
      "paridad": 1,
      "controlesPrenatales": 8,
      "semanasGestacion": 39.0,
      "hipertensionPrevia": 0,
      "diabetesGestacional": 0,
      "cesareaPrevia": 0,
      "embarazoMultiple": 0
    },
    {
      "edadMaterna": 35,
      "paridad": 2,
      "controlesPrenatales": 6,
      "semanasGestacion": 38.0,
      "hipertensionPrevia": 1,
      "diabetesGestacional": 0,
      "cesareaPrevia": 1,
      "embarazoMultiple": 0
    }
  ]
}
```

**Respuesta Exitosa (200):**
```json
{
  "resultados": [
    {
      "id_paciente": 0,
      "predicciones": [ /* ... */ ],
      "resumen": { /* ... */ },
      "datosPaciente": { /* ... */ }
    },
    {
      "id_paciente": 1,
      "predicciones": [ /* ... */ ],
      "resumen": { /* ... */ },
      "datosPaciente": { /* ... */ }
    }
  ],
  "estadisticas": {
    "total_pacientes": 2,
    "riesgos_altos": 1,
    "riesgos_moderados": 1,
    "riesgos_bajos": 0,
    "casos_urgentes": 1
  }
}
```

**Ejemplo curl:**
```bash
curl -X POST https://aluna-api.deployhero.dev/api/v1/predictions/batch \
  -H "Content-Type: application/json" \
  -d '{
    "pacientes": [
      {
        "edadMaterna": 28,
        "paridad": 1,
        "controlesPrenatales": 8,
        "semanasGestacion": 39.0,
        "hipertensionPrevia": 0,
        "diabetesGestacional": 0,
        "cesareaPrevia": 0,
        "embarazoMultiple": 0
      }
    ]
  }'
```

**Ejemplo JavaScript:**
```javascript
const predecirLote = async (pacientes) => {
  const response = await fetch('https://aluna-api.deployhero.dev/api/v1/predictions/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pacientes })
  });
  return await response.json();
};

const resultados = await predecirLote([
  { edadMaterna: 28, paridad: 1, /* ... */ },
  { edadMaterna: 35, paridad: 2, /* ... */ }
]);

console.log(resultados.estadisticas.casos_urgentes); // Número de casos urgentes
```

---

### 5. Predicción de Riesgo Específico

Predecir solo un tipo de riesgo específico.

**Endpoint:** `POST /api/v1/predictions/predict/{tipo_riesgo}`

**Tipos de riesgo disponibles:**
- `sepsis`
- `hipertension_gestacional`
- `hemorragia_posparto`

**Ejemplo:** `POST /api/v1/predictions/predict/sepsis`

**Body:** Mismo formato que predicción individual

**Respuesta Exitosa (200):**
```json
{
  "riesgo": "sepsis",
  "probabilidad": 0.2675,
  "nivelRiesgo": "muy_bajo",
  "nivelConfianza": "media",
  "recomendacion": "Seguimiento rutinario prenatal. Medidas preventivas estándar.",
  "datosPaciente": {
    "edadMaterna": 35,
    "paridad": 2,
    "controlesPrenatales": 6,
    "semanasGestacion": 38.0,
    "hipertensionPrevia": 1,
    "diabetesGestacional": 0,
    "cesareaPrevia": 1,
    "embarazoMultiple": 0
  }
}
```

**Ejemplo curl:**
```bash
curl -X POST https://aluna-api.deployhero.dev/api/v1/predictions/predict/hipertension_gestacional \
  -H "Content-Type: application/json" \
  -d '{ "edadMaterna": 35, ... }'
```

---

## 📊 Modelos de Datos

### PatientData (Request)

```typescript
interface PatientData {
  edadMaterna: number;          // 15-60
  paridad: number;              // 0-20
  controlesPrenatales: number;  // 0-20
  semanasGestacion: number;     // 4.0-45.0
  hipertensionPrevia: number;   // 0 o 1
  diabetesGestacional: number;  // 0 o 1
  cesareaPrevia: number;        // 0 o 1
  embarazoMultiple: number;     // 0 o 1
}
```

### RiskPrediction (Response)

```typescript
interface RiskPrediction {
  riesgo: 'sepsis' | 'hipertension_gestacional' | 'hemorragia_posparto';
  probabilidad: number;        // 0.0 - 1.0
  nivelRiesgo: 'muy_bajo' | 'bajo' | 'moderado' | 'alto';
  nivelConfianza: 'alta' | 'media' | 'baja';
  recomendacion: string;
}
```

### PredictionResponse (Response)

```typescript
interface PredictionResponse {
  predicciones: RiskPrediction[];
  resumen: {
    riesgo_general: 'muy_bajo' | 'bajo' | 'moderado' | 'alto';
    total_riesgos_altos: number;
    total_riesgos_moderados: number;
    total_riesgos_bajos: number;
    requiere_atencion_especial: boolean;
    riesgo_mas_alto: string;
    probabilidad_mas_alta: number;
  };
  datosPaciente: PatientData;
}
```

---

## 🎨 Códigos de Colores Sugeridos (UI)

**Niveles de Riesgo:**
- `muy_bajo`: 🟢 Verde (`#10B981`)
- `bajo`: 🟡 Amarillo Claro (`#FCD34D`)
- `moderado`: 🟠 Naranja (`#F59E0B`)
- `alto`: 🔴 Rojo (`#EF4444`)

**Confianza:**
- `alta`: 🟢 Verde
- `media`: 🟡 Amarillo
- `baja`: 🟠 Naranja

---

## ⚠️ Manejo de Errores

### 400 - Bad Request
```json
{
  "detail": "Descripción del error"
}
```

### 422 - Validation Error
```json
{
  "detail": [
    {
      "type": "int_type",
      "loc": ["body", "edadMaterna"],
      "msg": "Input should be a valid integer",
      "input": "invalid"
    }
  ]
}
```

### 500 - Internal Server Error
```json
{
  "detail": "Error interno del servidor"
}
```

**Ejemplo de manejo en JavaScript:**
```javascript
try {
  const resultado = await predecirRiesgos(datos);
  // Manejar resultado exitoso
} catch (error) {
  if (error.response) {
    // Error HTTP de la API
    switch (error.response.status) {
      case 422:
        console.error('Datos inválidos:', error.response.data.detail);
        break;
      case 500:
        console.error('Error del servidor');
        break;
      default:
        console.error('Error:', error.response.data.detail);
    }
  } else if (error.request) {
    // No hubo respuesta
    console.error('Sin respuesta del servidor');
  } else {
    // Error al configurar la petición
    console.error('Error:', error.message);
  }
}
```

---

## 🔐 CORS

La API tiene CORS habilitado para todos los orígenes (`*`) en desarrollo.

**Headers aceptados:**
- `Content-Type: application/json`
- `Accept: application/json`

---

## 📝 Notas Importantes

1. **Formato de Respuesta:** Todas las respuestas usan `camelCase` para las claves JSON
2. **Charset:** UTF-8 - Las recomendaciones incluyen acentos y caracteres especiales en español
3. **Límite Batch:** Máximo 100 pacientes por petición
4. **Performance:** Las predicciones son en tiempo real (~100-200ms por paciente)
5. **Cache:** Los modelos están pre-cargados en memoria para máxima velocidad

---

## 🧪 Casos de Prueba

### Caso 1: Riesgo Bajo
```json
{
  "edadMaterna": 28,
  "paridad": 1,
  "controlesPrenatales": 8,
  "semanasGestacion": 39.0,
  "hipertensionPrevia": 0,
  "diabetesGestacional": 0,
  "cesareaPrevia": 0,
  "embarazoMultiple": 0
}
```

### Caso 2: Riesgo Alto (Hipertensión)
```json
{
  "edadMaterna": 35,
  "paridad": 2,
  "controlesPrenatales": 6,
  "semanasGestacion": 38.0,
  "hipertensionPrevia": 1,
  "diabetesGestacional": 0,
  "cesareaPrevia": 1,
  "embarazoMultiple": 0
}
```

### Caso 3: Riesgo Alto (Múltiple)
```json
{
  "edadMaterna": 42,
  "paridad": 3,
  "controlesPrenatales": 4,
  "semanasGestacion": 36.5,
  "hipertensionPrevia": 1,
  "diabetesGestacional": 1,
  "cesareaPrevia": 1,
  "embarazoMultiple": 1
}
```

---

## 📞 Soporte

**Documentación Interactiva:** https://aluna-api.deployhero.dev/docs  
**Repositorio:** https://github.com/christianbueno1/aluna-api

---

Actualizado: Enero 2026
