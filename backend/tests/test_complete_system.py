"""
Tests exhaustivos para verificar que todo el sistema backend funciona correctamente
Especialmente integración con YOLO service, manejo de GPS y endpoints API
"""

import os
import sys
import pytest
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime
from fastapi.testclient import TestClient

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import get_settings
from app.models.enums import (
    RiskLevelEnum, DetectionRiskEnum, BreedingSiteTypeEnum,
    UserRoleEnum, LocationSourceEnum, ValidationStatusEnum
)
from app.utils.yolo_integration import (
    parse_yolo_detection, parse_yolo_report, validate_yolo_response
)
from app.services.yolo_service import YOLOServiceClient


def imprimir_encabezado_seccion(titulo):
    """Imprime encabezado formateado para salida de tests"""
    print(f"\n{'='*60}")
    print(f" {titulo}")
    print('='*60)


class TestConfiguracionSistema:
    """Tests para la configuración del sistema y dependencias"""

    def test_estructura_proyecto(self):
        """Test que la estructura del proyecto sea correcta"""
        imprimir_encabezado_seccion("TEST ESTRUCTURA DEL PROYECTO")

        raiz_proyecto = Path(__file__).parent.parent
        print(f"✓ Raíz del proyecto: {raiz_proyecto}")

        # Verificar archivos principales de la aplicación
        archivos_requeridos = [
            "app/main.py",
            "app/config.py",
            "app/database.py",
            "requirements.txt",
            "alembic.ini"
        ]

        for ruta_archivo in archivos_requeridos:
            ruta_completa = raiz_proyecto / ruta_archivo
            assert ruta_completa.exists(), f"Archivo requerido faltante: {ruta_archivo}"
            print(f"✓ Encontrado: {ruta_archivo}")

        # Verificar estructura de directorios
        directorios_requeridos = [
            "app/models",
            "app/api/v1",
            "app/schemas",
            "app/services",
            "app/utils",
            "tests",
            "alembic/versions"
        ]

        for ruta_dir in directorios_requeridos:
            ruta_completa = raiz_proyecto / ruta_dir
            assert ruta_completa.exists(), f"Directorio requerido faltante: {ruta_dir}"
            print(f"✓ Directorio: {ruta_dir}")

    def test_carga_configuracion(self):
        """Test carga de configuración"""
        imprimir_encabezado_seccion("TEST CONFIGURACIÓN")

        ajustes = get_settings()
        print(f"✓ URL Base de datos: {ajustes.database_url}")
        print(f"✓ URL Servicio YOLO: {ajustes.yolo_service_url}")
        print(f"✓ URL Redis: {ajustes.redis_url}")
        print(f"✓ Tamaño máximo archivo: {ajustes.max_file_size}")

        # Validar configuración
        assert ajustes.database_url is not None
        assert ajustes.yolo_service_url is not None
        assert ajustes.max_file_size > 0
        assert len(ajustes.allowed_extensions) > 0

    def test_completitud_enums(self):
        """Test que todos los enums estén definidos correctamente"""
        imprimir_encabezado_seccion("TEST COMPLETITUD DE ENUMS")

        # Test RiskLevelEnum
        niveles_riesgo = [e.value for e in RiskLevelEnum]
        print(f"✓ Niveles de riesgo: {niveles_riesgo}")
        assert "HIGH" in niveles_riesgo
        assert "MEDIUM" in niveles_riesgo

        # Test DetectionRiskEnum (debe coincidir con servicio YOLO)
        riesgos_deteccion = [e.value for e in DetectionRiskEnum]
        print(f"✓ Riesgos de detección: {riesgos_deteccion}")
        assert "ALTO" in riesgos_deteccion
        assert "MEDIO" in riesgos_deteccion
        assert "BAJO" in riesgos_deteccion

        # Test BreedingSiteTypeEnum (debe coincidir con clases YOLO)
        sitios_cria = [e.value for e in BreedingSiteTypeEnum]
        print(f"✓ Sitios de cría: {sitios_cria}")
        assert "Basura" in sitios_cria
        assert "Calles mal hechas" in sitios_cria
        assert "Charcos/Cumulo de agua" in sitios_cria
        assert "Huecos" in sitios_cria

        # Test UserRoleEnum
        roles_usuario = [e.value for e in UserRoleEnum]
        print(f"✓ Roles de usuario: {roles_usuario}")
        assert "admin" in roles_usuario
        assert "expert" in roles_usuario
        assert "user" in roles_usuario


class TestIntegracionServicioYOLO:
    """Tests para integración con servicio YOLO"""

    def test_parseo_respuesta_yolo(self):
        """Test funcionalidad de parseo de respuesta YOLO"""
        imprimir_encabezado_seccion("TEST PARSEO RESPUESTA YOLO")

        # Respuesta YOLO de ejemplo similar a la que retorna el servicio
        respuesta_yolo_ejemplo = {
            "success": True,
            "processing_time_ms": 1234,
            "model_version": "yolo11s-v1",
            "source": "test_image.jpg",
            "timestamp": "2025-09-19T10:30:00.123456",
            "camera_info": {
                "camera_make": "Xiaomi",
                "camera_model": "220333QL",
                "datetime_original": "2025:09:19 15:19:08"
            },
            "location": {
                "has_location": True,
                "latitude": -26.831314,
                "longitude": -65.195539,
                "location_source": "EXIF_GPS"
            },
            "detections": [
                {
                    "class_id": 0,
                    "class_name": "Basura",
                    "confidence": 0.75,
                    "risk_level": "MEDIO",
                    "polygon": [[100, 100], [200, 200]],
                    "mask_area": 10000.0,
                    "location": {
                        "has_location": True,
                        "latitude": -26.831314,
                        "longitude": -65.195539
                    }
                },
                {
                    "class_id": 2,
                    "class_name": "Charcos/Cumulo de agua",
                    "confidence": 0.85,
                    "risk_level": "ALTO",
                    "polygon": [[300, 300], [400, 400]],
                    "mask_area": 10000.0,
                    "location": {
                        "has_location": True,
                        "latitude": -26.831314,
                        "longitude": -65.195539
                    }
                }
            ],
            "risk_assessment": {
                "level": "ALTO",
                "high_risk_sites": 1,
                "medium_risk_sites": 1,
                "recommendations": ["Eliminación inmediata", "Monitoreo frecuente"]
            }
        }

        # Test validación
        es_valida = validate_yolo_response(respuesta_yolo_ejemplo)
        assert es_valida, "Respuesta YOLO de ejemplo debería ser válida"
        print("✓ Validación de respuesta YOLO exitosa")

        # Test parseo
        datos_parseados = parse_yolo_report(respuesta_yolo_ejemplo)
        print("✓ Parseo de respuesta YOLO completado")

        # Verificar datos de análisis parseados
        analisis = datos_parseados["analysis"]
        assert analisis["image_filename"] == "test_image.jpg"
        assert analisis["total_detections"] == 2
        assert analisis["has_gps_data"] is True
        assert analisis["risk_level"] == "HIGH"  # ALTO -> HIGH mapping
        print("✓ Datos de análisis parseados correctamente")

        # Verificar detecciones parseadas
        detecciones = datos_parseados["detections"]
        assert len(detecciones) == 2

        deteccion_basura = detecciones[0]
        assert deteccion_basura["class_name"] == "Basura"
        assert deteccion_basura["breeding_site_type"] == BreedingSiteTypeEnum.BASURA
        assert deteccion_basura["risk_level"] == DetectionRiskEnum.MEDIO

        deteccion_charcos = detecciones[1]
        assert deteccion_charcos["class_name"] == "Charcos/Cumulo de agua"
        assert deteccion_charcos["breeding_site_type"] == BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA
        assert deteccion_charcos["risk_level"] == DetectionRiskEnum.ALTO

        print("✓ Datos de detecciones parseados correctamente")

    def test_inicializacion_cliente_servicio_yolo(self):
        """Test que el cliente del servicio YOLO puede ser inicializado"""
        imprimir_encabezado_seccion("TEST CLIENTE SERVICIO YOLO")

        cliente = YOLOServiceClient()
        assert cliente.base_url is not None
        assert cliente.timeout > 0
        print(f"✓ Cliente YOLO inicializado con URL: {cliente.base_url}")

        # Test inicialización personalizada
        cliente_personalizado = YOLOServiceClient("http://localhost:9999", timeout=30.0)
        assert cliente_personalizado.base_url == "http://localhost:9999"
        assert cliente_personalizado.timeout == 30.0
        print("✓ Inicialización personalizada de cliente YOLO funciona")


class TestFlujoAPI:
    """Tests para flujo completo de API"""

    def test_flujo_analisis_completo(self):
        """Test flujo completo de análisis desde carga hasta resultados"""
        imprimir_encabezado_seccion("TEST FLUJO COMPLETO DE API")

        cliente = TestClient(app)

        # Test 1: Verificación de salud
        print("1. Probando endpoints de salud...")
        respuesta_salud = cliente.get("/api/v1/health")
        assert respuesta_salud.status_code == 200
        print("✓ Endpoint de salud funcionando")

        # Test 2: Crear análisis
        print("2. Probando creación de análisis...")
        imagen_ejemplo = b'\xff\xd8\xff\xe0' + b'\x00' * 1000  # JPEG mínimo
        archivos = {"file": ("test_image.jpg", imagen_ejemplo, "image/jpeg")}
        datos = {"confidence_threshold": 0.6, "include_gps": True}

        with pytest.MonkeyPatch().context() as m:
            # Mock servicio YOLO para este test
            async def detectar_mock(*args, **kwargs):
                return {
                    "success": True,
                    "yolo_response": {"detections": [], "success": True},
                    "parsed_data": {"analysis": {"total_detections": 0}, "detections": []}
                }

            from app.services.yolo_service import YOLOServiceClient
            m.setattr(YOLOServiceClient, "detect_image", detectar_mock)

            respuesta_crear = cliente.post("/api/v1/analyses", files=archivos, data=datos)
            assert respuesta_crear.status_code == 200
            datos_analisis = respuesta_crear.json()
            id_analisis = datos_analisis["analysis_id"]
            print(f"✓ Análisis creado con ID: {id_analisis}")

            # Test 3: Obtener análisis
            print("3. Probando obtención de análisis...")
            respuesta_obtener = cliente.get(f"/api/v1/analyses/{id_analisis}")
            assert respuesta_obtener.status_code == 200
            detalles_analisis = respuesta_obtener.json()
            assert detalles_analisis["id"] == id_analisis
            print("✓ Análisis obtenido exitosamente")

            # Test 4: Listar análisis
            print("4. Probando listado de análisis...")
            respuesta_lista = cliente.get("/api/v1/analyses")
            assert respuesta_lista.status_code == 200
            datos_lista = respuesta_lista.json()
            assert datos_lista["total"] >= 1
            print(f"✓ Encontrados {datos_lista['total']} análisis en la lista")

    def test_flujo_procesamiento_lote(self):
        """Test flujo de procesamiento en lote"""
        imprimir_encabezado_seccion("TEST FLUJO PROCESAMIENTO EN LOTE")

        cliente = TestClient(app)

        # Mock servicio YOLO
        with pytest.MonkeyPatch().context() as m:
            async def detectar_mock(*args, **kwargs):
                return {
                    "success": True,
                    "yolo_response": {"detections": [], "success": True},
                    "parsed_data": {"analysis": {"total_detections": 0}, "detections": []}
                }

            from app.services.yolo_service import YOLOServiceClient
            m.setattr(YOLOServiceClient, "detect_image", detectar_mock)

            # Test creación de lote
            datos_lote = {
                "image_urls": [
                    "https://example.com/imagen1.jpg",
                    "https://example.com/imagen2.jpg",
                    "https://example.com/imagen3.jpg"
                ],
                "confidence_threshold": 0.5,
                "include_gps": True
            }

            respuesta_lote = cliente.post("/api/v1/analyses/batch", json=datos_lote)
            assert respuesta_lote.status_code == 200
            resultado_lote = respuesta_lote.json()

            assert resultado_lote["total_images"] == 3
            assert len(resultado_lote["analyses"]) == 3
            print(f"✓ Lote creado con {resultado_lote['total_images']} imágenes")

            # Verificar que cada análisis fue creado
            for analisis in resultado_lote["analyses"]:
                assert "analysis_id" in analisis
                assert analisis["status"] == "pending"
            print("✓ Todos los análisis del lote creados exitosamente")

    def test_flujo_manejo_errores(self):
        """Test escenarios de manejo de errores"""
        imprimir_encabezado_seccion("TEST MANEJO DE ERRORES")

        cliente = TestClient(app)

        # Test 1: ID de análisis inválido
        id_falso = "00000000-0000-0000-0000-000000000000"
        respuesta = cliente.get(f"/api/v1/analyses/{id_falso}")
        assert respuesta.status_code == 404
        print("✓ Manejo de error 404 funciona")

        # Test 2: Validación de entrada inválida
        respuesta = cliente.post("/api/v1/analyses", data={})  # Sin archivo o URL
        assert respuesta.status_code == 400
        print("✓ Validación de entrada funciona")

        # Test 3: Tamaño de lote inválido
        lote_grande = {
            "image_urls": [f"https://example.com/imagen{i}.jpg" for i in range(51)],
            "confidence_threshold": 0.5
        }
        respuesta = cliente.post("/api/v1/analyses/batch", json=lote_grande)
        assert respuesta.status_code == 400
        print("✓ Validación de tamaño de lote funciona")


class TestIntegracionBaseDatos:
    """Tests para integración con base de datos"""

    def test_creacion_modelos_y_relaciones(self, db_session):
        """Test creación de modelos de base de datos y relaciones"""
        imprimir_encabezado_seccion("TEST MODELOS DE BASE DE DATOS")

        from app.models.models import UserProfile, Analysis, Detection
        import uuid

        # Crear usuario
        id_usuario = uuid.uuid4()
        usuario = UserProfile(
            id=id_usuario,
            role=UserRoleEnum.USER,
            display_name="Usuario de Prueba"
        )
        db_session.add(usuario)
        db_session.flush()
        print("✓ Usuario creado")

        # Crear análisis
        analisis = Analysis(
            user_id=id_usuario,
            image_url="https://test.com/imagen.jpg",
            has_gps_data=True,
            total_detections=2,
            risk_level=RiskLevelEnum.MEDIUM
        )
        db_session.add(analisis)
        db_session.flush()
        print("✓ Análisis creado")

        # Crear detecciones
        deteccion1 = Detection(
            analysis_id=analisis.id,
            class_id=0,
            class_name="Basura",
            confidence=0.75,
            risk_level=DetectionRiskEnum.MEDIO,
            breeding_site_type=BreedingSiteTypeEnum.BASURA
        )

        deteccion2 = Detection(
            analysis_id=analisis.id,
            class_id=2,
            class_name="Charcos/Cumulo de agua",
            confidence=0.85,
            risk_level=DetectionRiskEnum.ALTO,
            breeding_site_type=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA
        )

        db_session.add_all([deteccion1, deteccion2])
        db_session.commit()
        print("✓ Detecciones creadas")

        # Test relaciones
        usuario_obtenido = db_session.query(UserProfile).filter_by(id=id_usuario).first()
        assert len(usuario_obtenido.analyses) == 1
        print("✓ Relación Usuario-Análisis funciona")

        analisis_obtenido = db_session.query(Analysis).filter_by(id=analisis.id).first()
        assert len(analisis_obtenido.detections) == 2
        print("✓ Relación Análisis-Detección funciona")

        # Test valores de enums
        assert analisis_obtenido.risk_level == RiskLevelEnum.MEDIUM
        assert deteccion1.risk_level == DetectionRiskEnum.MEDIO
        assert deteccion1.breeding_site_type == BreedingSiteTypeEnum.BASURA
        print("✓ Valores de enums almacenados correctamente")


class TestRendimientoSistema:
    """Tests para características de rendimiento del sistema"""

    def test_peticiones_concurrentes(self):
        """Test manejo de peticiones concurrentes"""
        imprimir_encabezado_seccion("TEST PETICIONES CONCURRENTES")

        cliente = TestClient(app)

        # Mock servicio YOLO para test de rendimiento
        with pytest.MonkeyPatch().context() as m:
            async def detectar_mock(*args, **kwargs):
                await asyncio.sleep(0.01)  # Simular tiempo de procesamiento
                return {
                    "success": True,
                    "yolo_response": {"detections": [], "success": True},
                    "parsed_data": {"analysis": {"total_detections": 0}, "detections": []}
                }

            from app.services.yolo_service import YOLOServiceClient
            m.setattr(YOLOServiceClient, "detect_image", detectar_mock)

            # Test múltiples verificaciones de salud (deberían ser rápidas)
            tiempo_inicio = datetime.now()
            for _ in range(10):
                respuesta = cliente.get("/api/v1/health")
                assert respuesta.status_code == 200

            tiempo_salud = (datetime.now() - tiempo_inicio).total_seconds()
            print(f"✓ 10 verificaciones de salud completadas en {tiempo_salud:.2f}s")

            # Test múltiples creaciones de análisis
            imagen_ejemplo = b'\xff\xd8\xff\xe0' + b'\x00' * 100
            archivos = {"file": ("test.jpg", imagen_ejemplo, "image/jpeg")}

            tiempo_inicio = datetime.now()
            for i in range(5):
                respuesta = cliente.post("/api/v1/analyses", files=archivos)
                assert respuesta.status_code == 200

            tiempo_analisis = (datetime.now() - tiempo_inicio).total_seconds()
            print(f"✓ 5 creaciones de análisis completadas en {tiempo_analisis:.2f}s")

    def test_uso_memoria(self):
        """Test patrones básicos de uso de memoria"""
        imprimir_encabezado_seccion("TEST USO DE MEMORIA")

        import psutil
        import os

        proceso = psutil.Process(os.getpid())
        memoria_inicial = proceso.memory_info().rss / 1024 / 1024  # MB

        # Crear cliente de prueba y hacer peticiones
        cliente = TestClient(app)

        # Hacer múltiples peticiones para probar fugas de memoria
        for _ in range(100):
            cliente.get("/api/v1/health")

        memoria_final = proceso.memory_info().rss / 1024 / 1024  # MB
        incremento_memoria = memoria_final - memoria_inicial

        print(f"✓ Memoria inicial: {memoria_inicial:.1f} MB")
        print(f"✓ Memoria final: {memoria_final:.1f} MB")
        print(f"✓ Incremento de memoria: {incremento_memoria:.1f} MB")

        # Permitir incremento razonable de memoria por overhead de test
        assert incremento_memoria < 50, f"Incremento de memoria muy alto: {incremento_memoria:.1f} MB"


def ejecutar_test_completo_sistema():
    """Ejecutar todos los tests del sistema"""
    imprimir_encabezado_seccion("INICIANDO TEST COMPLETO DEL SISTEMA")

    # Importar todas las clases de test
    clases_test = [
        TestConfiguracionSistema,
        TestIntegracionServicioYOLO,
        TestFlujoAPI,
        TestIntegracionBaseDatos,
        TestRendimientoSistema
    ]

    tests_exitosos = 0
    total_tests = 0

    for clase_test in clases_test:
        nombre_clase = clase_test.__name__
        print(f"\n🧪 Ejecutando {nombre_clase}...")

        # Obtener todos los métodos de test
        metodos_test = [metodo for metodo in dir(clase_test) if metodo.startswith('test_')]

        for nombre_metodo in metodos_test:
            total_tests += 1
            try:
                # Crear instancia y ejecutar test
                instancia = clase_test()
                metodo = getattr(instancia, nombre_metodo)

                # Manejar fixtures de pytest para tests de base de datos
                if 'db_session' in metodo.__code__.co_varnames:
                    # Saltar tests de base de datos en ejecución independiente
                    print(f"    ⏭️  Saltando {nombre_metodo} (requiere pytest)")
                    continue

                metodo()
                tests_exitosos += 1
                print(f"    OK: {nombre_metodo}")

            except Exception as e:
                print(f"    ERROR: {nombre_metodo}: {e}")

    imprimir_encabezado_seccion("RESULTADOS DEL TEST DEL SISTEMA")
    print(f"OK: Exitosos: {tests_exitosos}")
    print(f"ERROR: Fallidos: {total_tests - tests_exitosos}")
    print(f"DATA: Tasa de éxito: {tests_exitosos/total_tests*100:.1f}%")

    return tests_exitosos == total_tests


if __name__ == "__main__":
    exito = ejecutar_test_completo_sistema()
    sys.exit(0 if exito else 1)