# Lógica de Evaluación de Riesgo - Sentrix

## Resumen

La evaluación de riesgo de criaderos del mosquito Aedes aegypti ahora considera **la diversidad de tipos de criaderos** además del número total de detecciones.

## Insight Clave

**Múltiples tipos diferentes de criaderos en la misma zona = Problema CRÍTICO (sistémico)**
**Mismo tipo repetido = Problema MENOR (localizado)**

### Ejemplo:

#### Escenario A: 5 detecciones del mismo tipo (Basura)
- **Riesgo**: BAJO
- **Razón**: Problema localizado, fácil de resolver (limpiar basura)
- **Diversidad**: 1 tipo único

#### Escenario B: 5 detecciones de tipos diferentes
- Basura
- Charcos/Cumulo de agua
- Huecos
- Calles mal hechas
- (otro criadero)

- **Riesgo**: ALTO/CRÍTICO
- **Razón**: Problema sistémico del área, múltiples condiciones favorables para reproducción
- **Diversidad**: 4+ tipos únicos

## Niveles de Riesgo

### 🔴 ALTO (Crítico)
Se activa cuando:
1. **3+ tipos diferentes** detectados con 4+ detecciones totales
   - Indica problema ambiental sistémico
2. **3+ sitios de alto riesgo** de 2+ tipos diferentes
   - Múltiples focos críticos diversos
3. **5+ sitios de alto riesgo** (incluso del mismo tipo)
   - Gran cantidad de focos peligrosos

**Recomendaciones especiales:**
- Si diversidad >= 3: "Múltiples tipos de criaderos detectados - problema sistémico del área"

### 🟡 MEDIO
Se activa cuando:
1. **2+ tipos diferentes** con al menos 1 alto riesgo o 2+ medio riesgo
2. **1+ sitio de alto riesgo** (sin importar diversidad)
3. **3+ sitios de medio riesgo** de 2+ tipos diferentes

**Recomendaciones especiales:**
- Si diversidad >= 2: "Diferentes tipos de criaderos detectados - revisar condiciones generales del área"

### 🟢 BAJO
Se activa cuando:
1. **1+ sitio de medio riesgo**
2. **3+ detecciones del mismo tipo único** (problema localizado)

**Recomendaciones especiales:**
- Si 1 tipo y 3+ detecciones: "Mismo tipo repetido - problema localizado, fácil de resolver"

### ⚪ MÍNIMO
- Muy pocas detecciones
- Sin patrones significativos

## Métricas Calculadas

### Nuevas métricas agregadas:
- `unique_types`: Número de tipos únicos de criaderos detectados
- `diversity_ratio`: Ratio de tipos únicos / total detecciones (0.0 - 1.0)
- `type_distribution`: Diccionario con conteo por tipo

### Ejemplo de respuesta:
```json
{
  "level": "ALTO",
  "risk_score": 0.92,
  "total_detections": 6,
  "high_risk_count": 3,
  "medium_risk_count": 3,
  "unique_types": 4,
  "diversity_ratio": 0.67,
  "type_distribution": {
    "Basura": 2,
    "Charcos/Cumulo de agua": 2,
    "Huecos": 1,
    "Calles mal hechas": 1
  },
  "recommendations": [
    "[ALERT] Intervención inmediata requerida",
    "[WATER] Eliminar agua estancada inmediatamente",
    "[CONTACT] Contactar autoridades sanitarias locales",
    "[STOP] Evitar acumulación de desechos",
    "[CRITICAL] Múltiples tipos de criaderos detectados - problema sistémico del área"
  ]
}
```

## Clasificación de Tipos de Criaderos

### Alto Riesgo (HIGH_RISK_CLASSES)
- **Charcos/Cumulo de agua**: Agua estancada = reproducción directa
- **Basura**: Acumulación de recipientes que retienen agua

### Medio Riesgo (MEDIUM_RISK_CLASSES)
- **Huecos**: Pueden acumular agua de lluvia
- **Calles mal hechas**: Baches que retienen agua

## Fórmulas de Riesgo

### Score Calculation

#### ALTO:
- Diversidad alta: `0.85 + (unique_types * 0.05)` max 1.0
- Alto riesgo diverso: `0.9 + (high_risk_count * 0.02)` max 1.0
- Muchos alto riesgo: `0.85 + (high_risk_count * 0.03)` max 1.0

#### MEDIO:
- Diversidad moderada: `0.5 + (unique_types * 0.05) + (high_risk_count * 0.1)`
- Con alto riesgo: `0.5 + (high_risk_count * 0.1) + (medium_risk_count * 0.05)`
- Medio riesgo diverso: `0.45 + (medium_risk_count * 0.05)`

#### BAJO:
- `0.25 + (total_detections * 0.02)`

#### MÍNIMO:
- `0.05 + (total_detections * 0.01)`

## Comparación: Antes vs Después

### Caso de Ejemplo: 5 Basuras

**ANTES:**
- Total: 5 detecciones
- Alto riesgo: 5
- **Resultado: ALTO** [ERROR] (incorrecto - es problema simple)

**DESPUÉS:**
- Total: 5 detecciones
- Alto riesgo: 5
- Tipos únicos: 1
- Diversidad: 0.2
- **Resultado: BAJO** [OK] (correcto - problema localizado)

### Caso de Ejemplo: 5 Tipos Diferentes

**ANTES:**
- Total: 5 detecciones
- Alto riesgo: 2
- **Resultado: MEDIO** [ERROR] (incorrecto - es muy grave)

**DESPUÉS:**
- Total: 5 detecciones
- Alto riesgo: 2
- Tipos únicos: 5
- Diversidad: 1.0
- **Resultado: ALTO** [OK] (correcto - problema sistémico)

## Implementación

Archivo: `shared/sentrix_shared/risk_assessment.py`
Función: `assess_dengue_risk(detections: List[Dict[str, Any]])`

**Backward compatible**: Los campos antiguos siguen disponibles para compatibilidad con código existente.

## Fecha de Implementación

30 de Octubre, 2025
