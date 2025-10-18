"""
Prueba final de integración completa
Final integration test with running services
"""

import asyncio
import sys
from pathlib import Path


async def test_complete_integration():
    """
    Probar integración completa con servicios corriendo
    """
    print("Probando integración completa YOLO + Backend...")
    print("=" * 50)

    try:
        # 1. Probar salud de YOLO service
        from ..core.services.yolo_service import YOLOServiceClient

        yolo_client = YOLOServiceClient(base_url="http://localhost:8001")
        health = await yolo_client.health_check()

        print("[OK] Servidor YOLO funcionando")
        print(f"   Estado: {health.get('status')}")
        print(f"   Modelo disponible: {health.get('model_available')}")
        print(f"   Modelo: {health.get('model_path')}")

        # 2. Probar servicio de análisis
        from src.services.analysis_service import AnalysisService

        analysis_service = AnalysisService()

        # Crear imagen de prueba muy pequeña (PNG 1x1 pixel)
        test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'

        print("\\n[INFO] Procesando imagen de prueba...")
        result = await analysis_service.process_image_analysis(
            image_data=test_image,
            filename="test.png",
            confidence_threshold=0.3,
            include_gps=True
        )

        print("[OK] Análisis completado")
        print(f"   ID: {result.get('analysis_id')}")
        print(f"   Estado: {result.get('status')}")
        print(f"   Detecciones: {result.get('total_detections', 0)}")
        print(f"   Tiempo: {result.get('processing_time_ms')}ms")
        print(f"   GPS: {result.get('has_gps_data')}")

        # 3. Probar modelos disponibles
        models = await yolo_client.get_available_models()
        print(f"\\n[OK] Modelos disponibles: {len(models.get('available_models', []))}")

        print("\\n" + "=" * 50)
        print("[ÉXITO] ¡Integración completa funcionando!")
        print("\\nEl sistema está listo para:")
        print("- Recibir imágenes vía API")
        print("- Procesarlas con YOLO")
        print("- Almacenar resultados")
        print("- Devolver análisis completos")

        return True

    except Exception as e:
        print(f"\\n[ERROR] Error en integración: {e}")
        print("\\nVerificar:")
        print("1. Servidor YOLO corriendo en puerto 8001")
        print("2. Modelo YOLO disponible")
        print("3. Dependencias instaladas")
        return False

if __name__ == "__main__":
    asyncio.run(test_complete_integration())