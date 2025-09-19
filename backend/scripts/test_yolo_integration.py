#!/usr/bin/env python3
"""
Script de prueba para verificar integración con YOLO Service
Prueba conectividad, respuesta y compatibilidad de datos
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Agregar directorio raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.yolo_service import YOLOServiceClient
from app.utils.yolo_integration import parse_yolo_report, validate_yolo_response
from app.models.enums import DetectionRiskEnum, BreedingSiteTypeEnum


def imprimir_encabezado(titulo):
    """Imprime encabezado formateado"""
    print(f"\n{'='*60}")
    print(f" {titulo}")
    print('='*60)


async def verificar_conectividad():
    """Verifica que el servicio YOLO esté disponible"""
    imprimir_encabezado("VERIFICACIÓN DE CONECTIVIDAD")

    cliente = YOLOServiceClient()
    print(f"🔗 URL del servicio YOLO: {cliente.base_url}")
    print(f"⏱️  Timeout configurado: {cliente.timeout}s")

    try:
        # Intentar conexión básica
        resultado = await cliente.health_check()
        if resultado:
            print("✅ Servicio YOLO disponible y respondiendo")
            return True
        else:
            print("❌ Servicio YOLO no responde correctamente")
            return False

    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        return False


def probar_parseo_respuesta():
    """Prueba el parseo de respuestas YOLO con datos de ejemplo"""
    imprimir_encabezado("PRUEBA DE PARSEO DE RESPUESTAS")

    # Respuesta YOLO de ejemplo que debería funcionar
    respuesta_ejemplo = {
        "success": True,
        "processing_time_ms": 1250,
        "model_version": "yolo11s-v1",
        "source": "imagen_prueba.jpg",
        "timestamp": "2025-09-19T10:30:00.123456",
        "location": {
            "has_location": True,
            "latitude": -26.831314,
            "longitude": -65.195539,
            "altitude_meters": 458.2,
            "gps_date": "2025:09:19",
            "location_source": "EXIF_GPS",
            "maps": {
                "google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539"
            }
        },
        "camera_info": {
            "camera_make": "Xiaomi",
            "camera_model": "220333QL",
            "datetime_original": "2025:09:19 15:19:08",
            "software": "MIUI Camera"
        },
        "risk_assessment": {
            "level": "ALTO",
            "high_risk_sites": 1,
            "medium_risk_sites": 1,
            "recommendations": ["Eliminación inmediata", "Monitoreo frecuente"]
        },
        "detections": [
            {
                "class_id": 0,
                "class": "Basura",
                "confidence": 0.75,
                "risk_level": "MEDIO",
                "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]],
                "mask_area": 10000.0,
                "location": {"has_location": False}
            },
            {
                "class_id": 2,
                "class": "Charcos/Cumulo de agua",
                "confidence": 0.85,
                "risk_level": "ALTO",
                "polygon": [[300, 300], [400, 300], [400, 400], [300, 400]],
                "mask_area": 15000.0,
                "location": {
                    "has_location": True,
                    "latitude": -26.831314,
                    "longitude": -65.195539
                }
            }
        ]
    }

    print("🧪 Probando validación de respuesta YOLO...")
    es_valida = validate_yolo_response(respuesta_ejemplo)
    if es_valida:
        print("✅ Respuesta YOLO válida")
    else:
        print("❌ Respuesta YOLO inválida")
        return False

    print("\n🔄 Probando parseo de respuesta...")
    try:
        datos_parseados = parse_yolo_report(respuesta_ejemplo)
        print("✅ Parseo exitoso")

        # Verificar análisis parseado
        analisis = datos_parseados["analysis"]
        print(f"📁 Archivo: {analisis['image_filename']}")
        print(f"🔢 Total detecciones: {analisis['total_detections']}")
        print(f"🌍 Tiene GPS: {analisis['has_gps_data']}")
        print(f"⚠️  Nivel de riesgo: {analisis['risk_level']}")

        # Verificar detecciones parseadas
        detecciones = datos_parseados["detections"]
        print(f"\n🦟 Detecciones procesadas: {len(detecciones)}")

        for i, deteccion in enumerate(detecciones, 1):
            print(f"  {i}. {deteccion['class_name']} - Confianza: {deteccion['confidence']:.2f}")
            print(f"     Tipo: {deteccion['breeding_site_type']}")
            print(f"     Riesgo: {deteccion['risk_level']}")
            print(f"     GPS: {'Sí' if deteccion['has_location'] else 'No'}")

        return True

    except Exception as e:
        print(f"❌ Error durante parseo: {e}")
        return False


def verificar_mapeos_enums():
    """Verifica que los mapeos entre YOLO y backend sean correctos"""
    imprimir_encabezado("VERIFICACIÓN DE MAPEOS DE ENUMS")

    from app.utils.yolo_integration import (
        CLASS_ID_TO_BREEDING_SITE,
        CLASS_NAME_TO_BREEDING_SITE,
        YOLO_RISK_TO_DETECTION_RISK
    )

    print("🏷️  Verificando mapeo de class_id a tipos de sitio de cría:")
    mapeos_correctos = 0
    for class_id, tipo_sitio in CLASS_ID_TO_BREEDING_SITE.items():
        print(f"  ID {class_id} -> {tipo_sitio.value}")
        mapeos_correctos += 1

    print(f"✅ {mapeos_correctos} mapeos de class_id configurados")

    print("\n📝 Verificando mapeo de nombres de clase:")
    mapeos_correctos = 0
    for nombre_clase, tipo_sitio in CLASS_NAME_TO_BREEDING_SITE.items():
        print(f"  '{nombre_clase}' -> {tipo_sitio.value}")
        mapeos_correctos += 1

    print(f"✅ {mapeos_correctos} mapeos de nombres configurados")

    print("\n⚠️  Verificando mapeo de niveles de riesgo:")
    mapeos_correctos = 0
    for riesgo_yolo, riesgo_backend in YOLO_RISK_TO_DETECTION_RISK.items():
        print(f"  '{riesgo_yolo}' -> {riesgo_backend.value}")
        mapeos_correctos += 1

    print(f"✅ {mapeos_correctos} mapeos de riesgo configurados")

    # Verificar que todos los enums necesarios estén cubiertos
    print("\n🔍 Verificando completitud de mapeos:")

    # Verificar que todos los tipos de sitio de YOLO estén mapeados
    tipos_esperados = ["Basura", "Calles mal hechas", "Charcos/Cumulo de agua", "Huecos"]
    tipos_mapeados = list(CLASS_NAME_TO_BREEDING_SITE.keys())

    faltantes = set(tipos_esperados) - set(tipos_mapeados)
    if faltantes:
        print(f"❌ Tipos de sitio sin mapear: {faltantes}")
    else:
        print("✅ Todos los tipos de sitio esperados están mapeados")

    # Verificar niveles de riesgo
    riesgos_esperados = ["BAJO", "MEDIO", "ALTO"]
    riesgos_mapeados = list(YOLO_RISK_TO_DETECTION_RISK.keys())

    faltantes = set(riesgos_esperados) - set(riesgos_mapeados)
    if faltantes:
        print(f"❌ Niveles de riesgo sin mapear: {faltantes}")
    else:
        print("✅ Todos los niveles de riesgo están mapeados")

    return len(faltantes) == 0


async def probar_deteccion_imagen():
    """Prueba detección real con una imagen si el servicio está disponible"""
    imprimir_encabezado("PRUEBA DE DETECCIÓN REAL")

    cliente = YOLOServiceClient()

    # Crear una imagen JPEG mínima para prueba
    imagen_prueba = b'\xff\xd8\xff\xe0' + b'\x00' * 1000  # JPEG básico

    try:
        print("📤 Enviando imagen de prueba al servicio YOLO...")
        resultado = await cliente.detect_image(
            image_data=imagen_prueba,
            filename="imagen_prueba.jpg",
            confidence_threshold=0.5,
            include_gps=True
        )

        if resultado["success"]:
            print("✅ Detección completada exitosamente")

            # Mostrar información del resultado
            respuesta_yolo = resultado["yolo_response"]
            datos_parseados = resultado["parsed_data"]

            print(f"⏱️  Tiempo de procesamiento: {respuesta_yolo.get('processing_time_ms', 'N/A')} ms")
            print(f"🤖 Modelo usado: {respuesta_yolo.get('model_version', 'N/A')}")

            analisis = datos_parseados["analysis"]
            print(f"🔢 Detecciones encontradas: {analisis['total_detections']}")

            if analisis['total_detections'] > 0:
                print("\n🦟 Detecciones:")
                for i, det in enumerate(datos_parseados["detections"], 1):
                    print(f"  {i}. {det['class_name']} - Confianza: {det['confidence']:.2f}")

            return True
        else:
            print(f"❌ Error en detección: {resultado.get('error', 'Error desconocido')}")
            return False

    except Exception as e:
        print(f"❌ Error durante prueba de detección: {e}")
        return False


async def main():
    """Función principal del script"""
    print("🔬 Script de Prueba de Integración YOLO - Sentrix Backend")
    print("=" * 60)

    # Ejecutar todas las pruebas
    pruebas = [
        ("Conectividad", verificar_conectividad),
        ("Parseo de respuestas", lambda: probar_parseo_respuesta()),
        ("Mapeos de enums", lambda: verificar_mapeos_enums()),
        ("Detección real", probar_deteccion_imagen)
    ]

    resultados = []

    for nombre, prueba in pruebas:
        print(f"\n🧪 Ejecutando prueba: {nombre}")
        try:
            if asyncio.iscoroutinefunction(prueba):
                resultado = await prueba()
            else:
                resultado = prueba()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en prueba {nombre}: {e}")
            resultados.append((nombre, False))

    # Resumen final
    imprimir_encabezado("RESUMEN DE PRUEBAS")

    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        estado = "✅ EXITOSA" if resultado else "❌ FALLÓ"
        print(f"  {nombre}: {estado}")

    print(f"\n📊 Resultado final: {exitosas}/{total} pruebas exitosas")

    if exitosas == total:
        print("🎉 ¡Todas las pruebas pasaron! La integración YOLO está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar configuración y conectividad.")

    return exitosas == total


if __name__ == "__main__":
    try:
        resultado = asyncio.run(main())
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Prueba cancelada por el usuario")
        sys.exit(1)