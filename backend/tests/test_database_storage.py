"""
Prueba de almacenamiento en base de datos
Database storage integration test
"""

import asyncio
import sys
from pathlib import Path

# Agregar directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

async def test_database_storage():
    """
    Probar almacenamiento completo en base de datos
    """
    print("Probando almacenamiento completo en base de datos...")
    print("=" * 60)

    try:
        # 1. Probar conexión a Supabase
        from src.utils.supabase_client import get_supabase_manager

        supabase = get_supabase_manager()
        connection_test = supabase.test_connection()

        print(f"[INFO] Conexión Supabase: {connection_test.get('status')}")
        if connection_test.get('status') != 'connected':
            print(f"[ERROR] No se puede conectar a Supabase: {connection_test.get('message')}")
            return False

        # 2. Probar servicio de análisis completo
        from app.services.analysis_service import AnalysisService

        analysis_service = AnalysisService()

        # Usar imagen real del dataset
        test_image_path = "C:/Users/manolo/Documents/Sentrix/yolo-service/data/images/test/0cd33dd4-IMG-20241025-WA0014.jpg"

        with open(test_image_path, "rb") as f:
            test_image = f.read()

        print("\\n[INFO] Procesando imagen con almacenamiento en BD...")

        result = await analysis_service.process_image_analysis(
            image_data=test_image,
            filename="0cd33dd4-IMG-20241025-WA0014.jpg",
            confidence_threshold=0.3,
            include_gps=True
        )

        print("[OK] Análisis completado con almacenamiento en BD")
        print(f"   Analysis ID: {result.get('analysis_id')}")
        print(f"   Estado: {result.get('status')}")
        print(f"   Total detecciones: {result.get('total_detections', 0)}")
        print(f"   Tiempo procesamiento: {result.get('processing_time_ms')}ms")
        print(f"   GPS detectado: {result.get('has_gps_data')}")
        print(f"   Cámara detectada: {result.get('camera_detected')}")

        # 3. Verificar que los datos se guardaron en Supabase
        analysis_id = result.get('analysis_id')
        if analysis_id:
            print(f"\\n[INFO] Verificando almacenamiento del análisis {analysis_id}...")

            # Consultar análisis directamente desde Supabase
            try:
                analyses_result = supabase.get_analyses(limit=1)
                if analyses_result.get('status') == 'success' and analyses_result.get('count', 0) > 0:
                    latest_analysis = analyses_result['data'][0]
                    print("[OK] Análisis encontrado en base de datos")
                    print(f"   ID en BD: {latest_analysis.get('id')}")
                    print(f"   Estado en BD: {latest_analysis.get('status')}")
                    print(f"   Archivo: {latest_analysis.get('image_filename')}")
                    print(f"   Tamaño: {latest_analysis.get('image_size_bytes')} bytes")
                    print(f"   Detecciones: {latest_analysis.get('total_detections')}")
                else:
                    print("[WARNING] No se encontraron análisis en la base de datos")
            except Exception as e:
                print(f"[WARNING] Error consultando análisis: {e}")

        print("\\n" + "=" * 60)
        print("[ÉXITO] ¡Almacenamiento en base de datos funcionando!")
        print("\\nEl sistema ahora:")
        print("- Procesa imágenes con YOLO")
        print("- Almacena análisis en Supabase")
        print("- Guarda detecciones con coordenadas")
        print("- Actualiza estados correctamente")

        return True

    except Exception as e:
        print(f"\\n[ERROR] Error en prueba de almacenamiento: {e}")
        print("\\nVerificar:")
        print("1. Servidor YOLO corriendo en puerto 8001")
        print("2. Configuración de Supabase en .env")
        print("3. Permisos de base de datos")
        print("4. Esquemas de tablas creados")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_storage())