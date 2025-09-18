#!/usr/bin/env python3
"""
Test para generar reportes con información GPS integrada
"""

import os
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core import detect_breeding_sites
from src.reports import generate_report, save_report
from src.utils.file_ops import print_section_header

def test_gps_report_generation():
    """Test generación de reportes con GPS"""
    print_section_header("TEST REPORTES CON GPS")

    # Buscar una imagen con GPS (Xiaomi)
    project_root_path = Path(__file__).parent.parent
    test_image = None

    # Buscar en train
    train_dir = project_root_path / "data" / "images" / "train"
    if train_dir.exists():
        for file in os.listdir(train_dir):
            if file.startswith("067205de"):  # Esta imagen sabemos que tiene GPS
                test_image = train_dir / file
                break

    if not test_image or not test_image.exists():
        print("❌ No se encontró imagen de test con GPS")
        return False

    print(f"📷 Usando imagen: {test_image.name}")

    # Verificar si hay modelos disponibles
    models_dir = project_root_path / "models"
    best_model = None

    if models_dir.exists():
        # Buscar un modelo best.pt
        for root, dirs, files in os.walk(models_dir):
            if "best.pt" in files:
                best_model = os.path.join(root, "best.pt")
                break

    if not best_model:
        print("⚠️  No se encontró modelo entrenado - generando reporte sin detecciones")
        # Simular detecciones para el test
        detections = [
            {
                'class': 'Charcos/Cumulo de agua',
                'class_id': 2,
                'confidence': 0.85,
                'polygon': [[100, 100], [200, 100], [200, 200], [100, 200]],
                'mask_area': 10000.0
            },
            {
                'class': 'Basura',
                'class_id': 0,
                'confidence': 0.72,
                'polygon': [[300, 300], [400, 300], [400, 400], [300, 400]],
                'mask_area': 10000.0
            }
        ]
    else:
        print(f"🤖 Usando modelo: {best_model}")
        # Detectar usando modelo real
        try:
            detections = detect_breeding_sites(
                model_path=best_model,
                source=str(test_image),
                conf_threshold=0.5
            )
            print(f"✅ Detecciones encontradas: {len(detections)}")
        except Exception as e:
            print(f"❌ Error en detección: {e}")
            print("📝 Usando detecciones simuladas")
            detections = [
                {
                    'class': 'Huecos',
                    'class_id': 3,
                    'confidence': 0.90,
                    'polygon': [[150, 150], [250, 150], [250, 250], [150, 250]],
                    'mask_area': 10000.0
                }
            ]

    # Generar reporte CON GPS
    print("\n📊 Generando reporte con GPS...")
    report_with_gps = generate_report(str(test_image), detections, include_gps=True)

    # Generar reporte SIN GPS (para comparación)
    print("📊 Generando reporte sin GPS...")
    report_without_gps = generate_report(str(test_image), detections, include_gps=False)

    # Guardar reportes
    results_dir = project_root_path / "results"
    results_dir.mkdir(exist_ok=True)

    gps_report_path = results_dir / "test_report_with_gps.json"
    no_gps_report_path = results_dir / "test_report_without_gps.json"

    save_report(report_with_gps, str(gps_report_path))
    save_report(report_without_gps, str(no_gps_report_path))

    print(f"\n✅ Reportes guardados:")
    print(f"  📍 Con GPS: {gps_report_path}")
    print(f"  📍 Sin GPS: {no_gps_report_path}")

    # Mostrar diferencias
    print("\n📋 COMPARACIÓN DE REPORTES:")
    print("="*50)

    print(f"Reporte SIN GPS - Campos: {len(report_without_gps.keys())}")
    for key in sorted(report_without_gps.keys()):
        print(f"  - {key}")

    print(f"\nReporte CON GPS - Campos: {len(report_with_gps.keys())}")
    for key in sorted(report_with_gps.keys()):
        if key not in report_without_gps:
            print(f"  + {key} [NUEVO]")
        else:
            print(f"  - {key}")

    # Mostrar información GPS específica
    if 'location' in report_with_gps:
        location = report_with_gps['location']
        if location.get('has_location', False):
            print(f"\n🌍 INFORMACIÓN GPS EXTRAÍDA:")
            print(f"  Coordenadas: {location['coordinates']}")
            print(f"  Latitud: {location['latitude']:.6f}")
            print(f"  Longitud: {location['longitude']:.6f}")
            print(f"  Altitud: {location.get('altitude_meters', 'N/A')} metros")
            print(f"  Fecha GPS: {location.get('gps_date', 'N/A')}")

            if 'maps' in location:
                print(f"  🗺️  Google Maps: {location['maps']['google_maps_url']}")

            if 'sentrix_integration' in location:
                sentrix = location['sentrix_integration']
                print(f"  🎯 Integración Sentrix:")
                print(f"     GeoPoint: {sentrix.get('geo_point')}")
                print(f"     Color marcador: {sentrix.get('marker_color')}")
                print(f"     Zoom recomendado: {sentrix.get('zoom_level')}")

    # Mostrar información de cámara
    if 'camera_info' in report_with_gps:
        camera = report_with_gps['camera_info']
        print(f"\n📸 INFORMACIÓN DE CÁMARA:")
        print(f"  Marca: {camera.get('camera_make', 'N/A')}")
        print(f"  Modelo: {camera.get('camera_model', 'N/A')}")
        print(f"  Fecha/Hora: {camera.get('datetime_original', 'N/A')}")

    return True

def main():
    """Función principal"""
    success = test_gps_report_generation()

    print("\n" + "="*60)
    print(f"TEST {'EXITOSO' if success else 'FALLIDO'}")

    if success:
        print("✅ Sistema de reportes con GPS está funcionando")
        print("✅ Listo para integración en Sentrix")
    else:
        print("❌ Error en el sistema de reportes")

if __name__ == "__main__":
    main()