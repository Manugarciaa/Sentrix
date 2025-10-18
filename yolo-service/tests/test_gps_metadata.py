#!/usr/bin/env python3
"""
Test para extracción de metadata GPS en imágenes del proyecto Sentrix
Mueve el script final de GPS a la carpeta tests y lo adapta para testing
"""

import os
import sys
from pathlib import Path
import exifread

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from ..utils.file_ops import print_section_header
except ImportError:
    def print_section_header(title):
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)

def extract_gps_metadata(image_path):
    """
    Extrae metadata GPS de una imagen usando exifread

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        tuple: (gps_data dict o None, status string)
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        # Buscar datos GPS
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            lat = convert_exif_coords(tags['GPS GPSLatitude'])
            lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))

            lon = convert_exif_coords(tags['GPS GPSLongitude'])
            lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))

            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon

            # Datos adicionales
            altitude = None
            if 'GPS GPSAltitude' in tags:
                alt_val = tags['GPS GPSAltitude']
                altitude = float(alt_val.values[0].num) / float(alt_val.values[0].den)

            gps_date = str(tags.get('GPS GPSDate', 'N/A'))
            gps_time = str(tags.get('GPS GPSTimeStamp', 'N/A'))

            return {
                'latitude': lat,
                'longitude': lon,
                'coordinates': f"{lat:.6f},{lon:.6f}",
                'altitude': altitude,
                'gps_date': gps_date,
                'gps_time': gps_time,
                'has_gps': True
            }, "GPS extracted successfully"

        return {'has_gps': False}, "No GPS coordinates in EXIF"

    except Exception as e:
        return {'has_gps': False}, f"Error: {str(e)}"

def convert_exif_coords(coords):
    """
    Convierte coordenadas EXIF DMS a formato decimal

    Args:
        coords: Objeto de coordenadas EXIF

    Returns:
        float: Coordenada en formato decimal
    """
    values = coords.values
    degrees = float(values[0].num) / float(values[0].den)
    minutes = float(values[1].num) / float(values[1].den)
    seconds = float(values[2].num) / float(values[2].den)
    return degrees + minutes/60 + seconds/3600

def get_camera_metadata(image_path):
    """
    Extrae información de cámara de la imagen

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        dict: Información de cámara
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        return {
            'make': str(tags.get('Image Make', 'N/A')),
            'model': str(tags.get('Image Model', 'N/A')),
            'datetime': str(tags.get('Image DateTime', 'N/A')),
            'software': str(tags.get('Image Software', 'N/A'))
        }
    except:
        return {
            'make': 'N/A',
            'model': 'N/A',
            'datetime': 'N/A',
            'software': 'N/A'
        }

def scan_project_images():
    """
    Escanea todas las imágenes del proyecto para análisis GPS

    Returns:
        list: Lista de rutas de imágenes encontradas
    """
    project_root = Path(__file__).parent.parent
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}

    all_images = []
    scan_dirs = [
        project_root / "data" / "images" / "train",
        project_root / "data" / "images" / "val",
        project_root / "data" / "images" / "test",
        project_root / "test_images"
    ]

    for directory in scan_dirs:
        if directory.exists():
            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        all_images.append(os.path.join(root, file))

    return sorted(all_images)

def test_gps_extraction():
    """
    Test principal para verificar extracción GPS en el dataset completo

    Returns:
        dict: Estadísticas de la extracción GPS
    """
    print_section_header("TEST GPS METADATA EXTRACTION")

    all_images = scan_project_images()
    print(f"\nAnalizando {len(all_images)} imagenes del proyecto...")

    # Estadísticas
    with_gps = []
    without_gps = []
    cameras = {}

    for i, image_path in enumerate(all_images, 1):
        # Información de cámara
        camera_info = get_camera_metadata(image_path)
        camera_key = f"{camera_info.get('make', 'N/A')} {camera_info.get('model', 'N/A')}"
        cameras[camera_key] = cameras.get(camera_key, 0) + 1

        # GPS
        gps_data, status = extract_gps_metadata(image_path)

        if gps_data.get('has_gps', False):
            with_gps.append({
                'file': os.path.basename(image_path),
                'coords': gps_data['coordinates'],
                'camera': camera_key,
                'altitude': gps_data.get('altitude'),
                'date': gps_data.get('gps_date')
            })
        else:
            without_gps.append({
                'file': os.path.basename(image_path),
                'camera': camera_key,
                'status': status
            })

    # Generar estadísticas
    stats = {
        'total_images': len(all_images),
        'with_gps': len(with_gps),
        'without_gps': len(without_gps),
        'gps_percentage': len(with_gps)/len(all_images)*100 if all_images else 0,
        'cameras': cameras,
        'gps_images': with_gps,
        'no_gps_images': without_gps
    }

    # Mostrar resultados
    print(f"\n[ESTADISTICAS]")
    print(f"  Total imagenes: {stats['total_images']}")
    print(f"  Con GPS: {stats['with_gps']} ({stats['gps_percentage']:.1f}%)")
    print(f"  Sin GPS: {stats['without_gps']} ({100-stats['gps_percentage']:.1f}%)")

    print(f"\n[CAMARAS DETECTADAS]")
    for camera, count in cameras.items():
        gps_count = len([img for img in with_gps if img['camera'] == camera])
        print(f"  {camera}: {count} imagenes ({gps_count} con GPS)")

    if with_gps:
        print(f"\n[PRIMERAS IMAGENES CON GPS]")
        for img in with_gps[:5]:
            print(f"  {img['file']}: {img['coords']} (Alt: {img.get('altitude', 'N/A')}m)")
        if len(with_gps) > 5:
            print(f"  ... y {len(with_gps)-5} mas")

    print(f"\n[CONCLUSION]")
    if len(with_gps) > 0:
        print(f"  [OK] {len(with_gps)} imagenes tienen geolocalizacion util")
        print("  [OK] Pueden usarse para mapeo de criaderos en Sentrix")

        # Calcular centro geográfico aproximado
        if with_gps:
            lats = [float(img['coords'].split(',')[0]) for img in with_gps]
            lons = [float(img['coords'].split(',')[1]) for img in with_gps]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            print(f"  [OK] Centro geografico aproximado: {center_lat:.4f},{center_lon:.4f}")
    else:
        print("  [WARN] Ninguna imagen tiene geolocalizacion")

    return stats

def test_specific_gps_extraction():
    """
    Test específico para verificar extracción GPS en imágenes conocidas
    """
    print_section_header("TEST SPECIFIC GPS SAMPLES")

    # Buscar algunas imágenes específicas para test
    project_root = Path(__file__).parent.parent
    test_samples = []

    # Buscar imágenes Xiaomi (deberían tener GPS)
    train_dir = project_root / "data" / "images" / "train"
    if train_dir.exists():
        for file in os.listdir(train_dir):
            if file.startswith("067205de") or file.startswith("7fb193cb"):
                test_samples.append(train_dir / file)
                if len(test_samples) >= 2:
                    break

    # Buscar imágenes Nothing (no deberían tener GPS)
    for file in os.listdir(train_dir) if train_dir.exists() else []:
        if file.startswith("04c22c36"):
            test_samples.append(train_dir / file)
            break

    success_tests = 0
    total_tests = len(test_samples)

    for image_path in test_samples:
        if image_path.exists():
            print(f"\n[TEST] {image_path.name}")
            gps_data, status = extract_gps_metadata(str(image_path))
            camera_info = get_camera_metadata(str(image_path))

            print(f"  Camera: {camera_info['make']} {camera_info['model']}")

            if gps_data.get('has_gps', False):
                print(f"  [PASS] GPS: {gps_data['coordinates']}")
                print(f"  [INFO] Altitude: {gps_data.get('altitude', 'N/A')}m")
                success_tests += 1
            else:
                print(f"  [EXPECTED] No GPS: {status}")
                # Para Nothing phones, no tener GPS es esperado
                if 'Nothing' in camera_info.get('make', ''):
                    success_tests += 1

    print(f"\n[RESULTADO TEST ESPECIFICO]")
    print(f"  Tests pasados: {success_tests}/{total_tests}")

    return success_tests == total_tests

if __name__ == "__main__":
    """
    Ejecutar tests de GPS cuando se llama directamente
    """
    # Test completo del dataset
    stats = test_gps_extraction()

    # Test específico de muestras
    specific_test_passed = test_specific_gps_extraction()

    # Resumen final
    print_section_header("RESUMEN FINAL DE TESTS")
    print(f"Dataset GPS analysis: {stats['with_gps']}/{stats['total_images']} imagenes con GPS")
    print(f"Specific samples test: {'PASSED' if specific_test_passed else 'FAILED'}")
    print(f"GPS extraction ready for integration: {'YES' if stats['with_gps'] > 0 else 'NO'}")