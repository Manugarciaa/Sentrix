# Sentrix Testing Guide
## Guía de Pruebas para Sentrix

Esta guía explica cómo ejecutar las pruebas exhaustivas para el nuevo sistema de procesamiento de imágenes.

## 🚀 Scripts de Pruebas Disponibles

### 1. Smoke Tests (Pruebas Rápidas)
```bash
python scripts/quick_smoke_tests.py
```

**Propósito**: Verificar que la funcionalidad básica funciona correctamente.
**Tiempo**: ~30 segundos
**Cuándo usar**: Antes de hacer cambios importantes o después de setup inicial.

**Qué prueba**:
- ✅ Importación de módulos críticos
- ✅ Generación de nombres estandarizados
- ✅ Detección de formatos de imagen
- ✅ Creación de clientes Supabase y YOLO
- ✅ Estructura del servicio de análisis
- ✅ Variaciones de nombres de archivo

### 2. Comprehensive Tests (Pruebas Exhaustivas)
```bash
python scripts/run_comprehensive_tests.py
```

**Propósito**: Ejecutar todas las pruebas del sistema completo.
**Tiempo**: ~5-10 minutos
**Cuándo usar**: Antes de hacer deploy o después de cambios significativos.

**Qué prueba**:
- 🧪 **Sistema de Nomenclatura** (100+ tests)
- 🗄️ **Almacenamiento Dual** (50+ tests)
- 🤖 **Integración YOLO-Backend** (75+ tests)
- ⚡ **Rendimiento y Carga** (25+ tests)
- 🚨 **Casos Extremos y Errores** (60+ tests)

## 📊 Interpretación de Resultados

### Resultado Exitoso ✅
```
🎉 OVERALL STATUS: ALL TESTS PASSED
📈 Success Rate: 100%
```
**Acción**: ¡Sistema listo para producción!

### Resultado con Problemas ⚠️
```
⚠️  OVERALL STATUS: ISSUES FOUND
📈 Success Rate: 85%
```
**Acción**: Revisar fallos específicos y corregir antes de continuar.

## 🔧 Instalación de Dependencias

```bash
# Dependencias básicas para tests
pip install pytest unittest2 psutil

# Para coverage (opcional)
pip install coverage

# Dependencias del proyecto
pip install -r backend/requirements.txt
pip install -r yolo-service/requirements.txt
```

## 📋 Categorías de Pruebas Detalladas

### 1. Tests de Nomenclatura Estandarizada
- **Archivo**: `shared/tests/test_standardized_naming.py`
- **Enfoque**: Generación y parsing de nombres de archivo
- **Casos críticos**:
  - Detección de dispositivos (iPhone, Samsung, Canon, etc.)
  - Codificación de coordenadas GPS
  - Manejo de caracteres especiales
  - Unicidad de IDs generados

### 2. Tests de Almacenamiento Dual
- **Archivo**: `backend/tests/test_dual_image_storage.py`
- **Enfoque**: Subida y gestión de imágenes en Supabase
- **Casos críticos**:
  - Upload de imagen original y procesada
  - Limpieza en caso de fallos parciales
  - Manejo de diferentes tipos MIME
  - Gestión de errores de red

### 3. Tests de Integración YOLO-Backend
- **Archivo**: `backend/tests/test_yolo_backend_integration.py`
- **Enfoque**: Comunicación entre servicios
- **Casos críticos**:
  - Procesamiento completo end-to-end
  - Manejo de timeouts y errores de conexión
  - Respuestas malformadas de YOLO
  - Rollback en caso de fallos

### 4. Tests de Rendimiento
- **Archivo**: `backend/tests/test_performance_load.py`
- **Enfoque**: Comportamiento bajo carga
- **Casos críticos**:
  - Procesamiento concurrente (50+ requests)
  - Uso de memoria y recursos
  - Detección de memory leaks
  - Benchmarks de operaciones críticas

### 5. Tests de Casos Extremos
- **Archivo**: `backend/tests/test_edge_cases_errors.py`
- **Enfoque**: Manejo de situaciones extremas
- **Casos críticos**:
  - Archivos corruptos o vacíos
  - Coordenadas GPS extremas
  - Nombres de archivo muy largos
  - Fallos de base de datos

## 🎯 Métricas de Calidad Esperadas

| Métrica | Objetivo | Crítico |
|---------|----------|---------|
| Success Rate | ≥ 95% | ≥ 90% |
| Coverage | ≥ 80% | ≥ 70% |
| Performance | < 3s per request | < 5s per request |
| Memory Leak | < 10MB growth | < 50MB growth |
| Concurrent Users | 50+ simultaneous | 20+ simultaneous |

## 🚨 Troubleshooting

### Problema: "Module not found"
```bash
# Verificar paths
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/backend/src:$(pwd)/shared"
```

### Problema: "Supabase connection failed"
- **Smoke tests**: Normal, solo verifica estructura
- **Comprehensive tests**: Revisa variables de entorno

### Problema: "YOLO service timeout"
- **Smoke tests**: Normal, solo verifica estructura
- **Comprehensive tests**: Verifica que yolo-service esté ejecutándose

### Problema: Tests muy lentos
```bash
# Ejecutar solo categoría específica
python -m pytest backend/tests/test_standardized_naming.py -v
```

## 📈 Reportes Generados

Después de ejecutar `run_comprehensive_tests.py`, se genera:

### 1. Reporte en Consola
- Resumen ejecutivo
- Resultados por suite
- Análisis de rendimiento
- Recomendaciones

### 2. Reporte JSON (`test_report.json`)
```json
{
  "timestamp": "2025-09-26T14:30:52",
  "system_info": {...},
  "summary": {
    "total_tests": 310,
    "total_passed": 305,
    "total_failed": 5,
    "success_rate": 98.4
  },
  "suites": [...]
}
```

## 🔄 Flujo de Trabajo Recomendado

### Durante Desarrollo
1. **Antes de cambios**: `python scripts/quick_smoke_tests.py`
2. **Después de cambios**: `python scripts/quick_smoke_tests.py`
3. **Antes de commit**: `python scripts/run_comprehensive_tests.py`

### Antes de Deploy
1. **Full test suite**: `python scripts/run_comprehensive_tests.py`
2. **Revisar coverage**: Verificar que esté ≥ 80%
3. **Revisar performance**: Verificar benchmarks
4. **Manual testing**: Probar casos de usuario real

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
- name: Run Smoke Tests
  run: python scripts/quick_smoke_tests.py

- name: Run Comprehensive Tests
  run: python scripts/run_comprehensive_tests.py

- name: Upload Test Report
  uses: actions/upload-artifact@v2
  with:
    name: test-report
    path: test_report.json
```

## 💡 Mejores Prácticas

### Para Desarrolladores
- ✅ Ejecutar smoke tests antes de cada commit
- ✅ Ejecutar tests completos antes de PR
- ✅ Revisar coverage de código nuevo
- ✅ Agregar tests para nuevas funcionalidades

### Para QA
- ✅ Ejecutar tests completos en cada build
- ✅ Verificar métricas de performance
- ✅ Documentar fallos encontrados
- ✅ Validar correcciones con re-testing

### Para DevOps
- ✅ Integrar tests en pipeline CI/CD
- ✅ Monitorear métricas de performance
- ✅ Alertar en degradación de coverage
- ✅ Automatizar reportes de calidad

## 📞 Soporte

Si encuentras problemas con las pruebas:

1. **Revisar logs**: Los tests generan output detallado
2. **Verificar dependencias**: Asegurar que todos los paquetes estén instalados
3. **Revisar configuración**: Variables de entorno y rutas
4. **Consultar documentación**: Este archivo y comentarios en código

¡Las pruebas exhaustivas garantizan que el sistema funcione correctamente en producción! 🚀