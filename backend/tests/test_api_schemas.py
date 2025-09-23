"""
Pruebas de esquemas de API y funcionalidad de endpoints
"""

import pytest
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_import_schemas():
    """Probar que todos los esquemas se pueden importar correctamente"""
    try:
        from app.schemas.analyses import (
            LocationData, CameraInfo, RiskAssessment, DetectionData,
            AnalysisUploadRequest, BatchUploadRequest, AnalysisUploadResponse,
            AnalysisResponse, AnalysisListQuery, AnalysisListResponse,
            BatchUploadResponse, AnalysisCreate, DetectionResponse,
            ErrorResponse, ValidationErrorResponse, HealthResponse
        )
        print("[OK] Todos los esquemas se importaron correctamente")
        return True
    except ImportError as e:
        print(f"[ERROR] Error al importar esquemas: {e}")
        return False

def test_settings_configuration():
    """Probar que las configuraciones se pueden cargar sin errores"""
    try:
        from config.settings import get_settings
        settings = get_settings()
        print("[OK] Configuraciones cargadas correctamente")
        print(f"   URL de base de datos configurada: {'Sí' if settings.database.url else 'No'}")
        print(f"   Host de API: {settings.api.host}:{settings.api.port}")
        print(f"   URL del servicio YOLO: {settings.external_services.yolo_service_url}")
        return True
    except Exception as e:
        print(f"[ERROR] Error en configuración: {e}")
        return False

def test_yolo_service_import():
    """Probar importación del cliente del servicio YOLO"""
    try:
        from app.services.yolo_service import YOLOServiceClient
        print("[OK] Cliente del servicio YOLO importado correctamente")
        return True
    except ImportError as e:
        print(f"[ERROR] Error al importar servicio YOLO: {e}")
        return False

def test_core_services_import():
    """Probar importación de servicios principales"""
    try:
        from src.core.services.yolo_service import YOLOServiceClient as CoreYOLOServiceClient
        print("[OK] Servicio YOLO principal importado correctamente")
        return True
    except ImportError as e:
        print(f"[ERROR] Error al importar servicios principales: {e}")
        return False

def test_schema_validation():
    """Probar validación de esquemas con datos de ejemplo"""
    try:
        from app.schemas.analyses import AnalysisUploadRequest, LocationData

        # Probar AnalysisUploadRequest
        request_data = {
            "image_url": "https://example.com/image.jpg",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "confidence_threshold": 0.7,
            "include_gps": True
        }
        request = AnalysisUploadRequest(**request_data)
        print("[OK] Validación de AnalysisUploadRequest exitosa")

        # Probar LocationData
        location_data = {
            "has_location": True,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "coordinates": "40.7128,-74.0060",
            "altitude_meters": 10.5,
            "location_source": "GPS"
        }
        location = LocationData(**location_data)
        print("[OK] Validación de LocationData exitosa")

        return True
    except Exception as e:
        print(f"[ERROR] Error en validación de esquemas: {e}")
        return False

if __name__ == "__main__":
    print("Probando esquemas de API y configuración...")
    print("=" * 50)

    tests = [
        test_import_schemas,
        test_settings_configuration,
        test_yolo_service_import,
        test_core_services_import,
        test_schema_validation
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
        print("[ÉXITO] Todas las pruebas de esquemas de API pasaron correctamente!")
    else:
        print("[FALLO] Algunas pruebas fallaron. Revisa el resultado arriba.")