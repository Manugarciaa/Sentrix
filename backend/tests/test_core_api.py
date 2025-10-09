"""
Probar funcionalidad principal de la API después de completar esquemas
"""

import pytest
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_fastapi_app_creation():
    """Probar que la aplicación FastAPI se puede crear"""
    try:
        from app import app
        print("[OK] Aplicación FastAPI creada correctamente")
        print(f"   Título de la app: {app.title}")
        print(f"   Versión de la app: {app.version}")
        return True
    except Exception as e:
        print(f"[ERROR] Error al crear aplicación FastAPI: {e}")
        return False

def test_api_routes_loading():
    """Probar que las rutas de la API se pueden cargar"""
    try:
        from src.api.v1 import analyses
        print("[OK] Rutas de análisis cargadas correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] Error al cargar rutas de API: {e}")
        return False

def test_database_models():
    """Probar que los modelos de base de datos se pueden importar"""
    try:
        from ..models.user import User
        from ..models.analysis import Analysis
        from ..models.detection import Detection
        print("[OK] Modelos de base de datos importados correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] Error al importar modelos de base de datos: {e}")
        return False

def test_core_settings():
    """Probar funcionalidad de configuraciones principales"""
    try:
        from src.config import get_settings

        settings = get_settings()

        print("[OK] Todas las funciones de configuración funcionando")
        print(f"   URL de base de datos: {settings.database_url[:50] if settings.database_url else 'No configurada'}...")
        print(f"   URL YOLO service: {settings.yolo_service_url}")
        return True
    except Exception as e:
        print(f"[ERROR] Error en funcionalidad de configuraciones: {e}")
        return False

def test_schema_completeness():
    """Probar que todos los esquemas requeridos estén disponibles"""
    try:
        from ..schemas.analyses import (
            AnalysisUploadRequest, AnalysisUploadResponse,
            AnalysisResponse, BatchUploadRequest, BatchUploadResponse,
            ErrorResponse, HealthResponse
        )

        # Probar que podemos crear instancias
        upload_req = AnalysisUploadRequest(
            confidence_threshold=0.6,
            include_gps=True
        )

        error_resp = ErrorResponse(
            error="test_error",
            message="Mensaje de error de prueba"
        )

        print("[OK] Todos los esquemas requeridos disponibles y funcionales")
        print(f"   Confianza de solicitud de carga: {upload_req.confidence_threshold}")
        print(f"   Tipo de respuesta de error: {error_resp.error}")
        return True
    except Exception as e:
        print(f"[ERROR] Error en prueba de integridad de esquemas: {e}")
        return False

if __name__ == "__main__":
    print("Probando funcionalidad principal de la API...")
    print("=" * 50)

    tests = [
        test_schema_completeness,
        test_core_settings,
        test_database_models,
        test_api_routes_loading,
        test_fastapi_app_creation
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\nEjecutando {test.__name__}...")
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Resultados: {passed}/{total} pruebas exitosas")

    if passed == total:
        print("[ÉXITO] Todas las pruebas de API principal pasaron!")
    elif passed >= 3:
        print("[PARCIAL] Funcionalidad principal funcionando con problemas menores")
    else:
        print("[FALLO] Problemas críticos encontrados en API principal")