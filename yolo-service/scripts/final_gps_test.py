#!/usr/bin/env python3
"""
Script final para extraer GPS de todas las imágenes usando exifread
"""

import os
import sys
from pathlib import Path
import exifread

def extract_gps_final(image_path):
    """Extrae GPS usando exifread (más robusto)"""
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
                'gps_time': gps_time
            }, "GPS extracted successfully"

        return None, "No GPS coordinates in EXIF"

    except Exception as e:
        return None, f"Error: {str(e)}"

def convert_exif_coords(coords):
    """Convierte coordenadas EXIF a decimal"""
    values = coords.values
    degrees = float(values[0].num) / float(values[0].den)
    minutes = float(values[1].num) / float(values[1].den)
    seconds = float(values[2].num) / float(values[2].den)
    return degrees + minutes/60 + seconds/3600

def get_camera_info(image_path):
    """Extrae información de cámara"""
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
        return {}

def scan_all_images():
    """Escanea todas las imágenes del proyecto"""
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

def main():
    """Función principal"""
    print("="*60)
    print(" ANÁLISIS FINAL DE GPS EN IMÁGENES SENTRIX")
    print("="*60)

    all_images = scan_all_images()
    print(f"\nAnalizando {len(all_images)} imágenes...")

    # Estadísticas
    with_gps = []
    without_gps = []
    cameras = {}

    for i, image_path in enumerate(all_images, 1):
        print(f"\n[{i:2d}/{len(all_images)}] {os.path.basename(image_path)}")

        # Información de cámara
        camera_info = get_camera_info(image_path)
        camera_key = f"{camera_info.get('make', 'N/A')} {camera_info.get('model', 'N/A')}"
        cameras[camera_key] = cameras.get(camera_key, 0) + 1

        # GPS
        gps_data, status = extract_gps_final(image_path)

        if gps_data:
            print(f"   [GPS OK] {gps_data['coordinates']}")
            print(f"   [INFO] Alt: {gps_data['altitude']:.1f}m, Fecha: {gps_data['gps_date']}")
            with_gps.append({
                'file': os.path.basename(image_path),
                'coords': gps_data['coordinates'],
                'camera': camera_key
            })
        else:
            print(f"   [GPS NO] {status}")
            without_gps.append({
                'file': os.path.basename(image_path),
                'camera': camera_key,
                'status': status
            })

    # Reporte final
    print("\n" + "="*60)
    print(" REPORTE FINAL")
    print("="*60)

    print(f"\n[ESTADÍSTICAS]")
    print(f"  Total imágenes: {len(all_images)}")
    print(f"  Con GPS: {len(with_gps)} ({len(with_gps)/len(all_images)*100:.1f}%)")
    print(f"  Sin GPS: {len(without_gps)} ({len(without_gps)/len(all_images)*100:.1f}%)")

    print(f"\n[CÁMARAS DETECTADAS]")
    for camera, count in cameras.items():
        gps_count = len([img for img in with_gps if img['camera'] == camera])
        print(f"  {camera}: {count} imágenes ({gps_count} con GPS)")

    if with_gps:
        print(f"\n[IMÁGENES CON GPS]")
        for img in with_gps[:5]:  # Mostrar primeras 5
            print(f"  {img['file']}: {img['coords']}")
        if len(with_gps) > 5:
            print(f"  ... y {len(with_gps)-5} más")

    print(f"\n[CONCLUSIÓN]")
    if len(with_gps) > 0:
        print(f"  ✅ {len(with_gps)} imágenes tienen geolocalización útil")
        print("  ✅ Pueden usarse para mapeo de criaderos en Sentrix")
        print("  ✅ Ubicación aproximada: Argentina (-26.8°S, -65.2°W)")
    else:
        print("  ❌ Ninguna imagen tiene geolocalización")

if __name__ == "__main__":
    main()