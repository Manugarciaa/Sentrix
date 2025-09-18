#!/usr/bin/env python3
"""
Test script para verificar metadata GPS en imágenes del proyecto
Revisa todas las imágenes y muestra cuáles tienen geolocalización
"""

import os
import sys
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from src.utils.file_ops import print_section_header
except ImportError:
    def print_section_header(title):
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)

def extract_gps_from_image(image_path):
    """Extrae coordenadas GPS de metadata EXIF"""
    try:
        with Image.open(image_path) as image:
            exifdata = image.getexif()

            if not exifdata:
                return None, "No EXIF data"

            # Buscar datos GPS
            for tag_id, value in exifdata.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    gps_coords = parse_gps_info(value)
                    if gps_coords:
                        return gps_coords, "GPS found"
                    else:
                        return None, "GPS data malformed"

            return None, "No GPS in EXIF"

    except Exception as e:
        return None, f"Error: {str(e)}"

def parse_gps_info(gps_info):
    """Convierte datos GPS a coordenadas decimales"""
    try:
        gps_data = {}
        for key, value in gps_info.items():
            name = GPSTAGS.get(key, key)
            gps_data[name] = value

        if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
            lat = convert_to_decimal(
                gps_data['GPSLatitude'],
                gps_data.get('GPSLatitudeRef', 'N')
            )
            lon = convert_to_decimal(
                gps_data['GPSLongitude'],
                gps_data.get('GPSLongitudeRef', 'E')
            )

            return {
                'latitude': lat,
                'longitude': lon,
                'coordinates': f"{lat:.6f},{lon:.6f}"
            }
    except Exception as e:
        print(f"Error parsing GPS: {e}")

    return None

def convert_to_decimal(coords, ref):
    """Convierte coordenadas DMS a decimal"""
    try:
        # Manejar diferentes formatos de coordenadas
        if isinstance(coords, (list, tuple)) and len(coords) == 3:
            degrees = float(coords[0])
            minutes = float(coords[1])
            seconds = float(coords[2])
            decimal = degrees + minutes/60 + seconds/3600
        else:
            decimal = float(coords)

        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception as e:
        print(f"Error converting coordinates: {e}")
        return 0.0

def get_other_exif_data(image_path):
    """Extrae otra metadata relevante"""
    try:
        with Image.open(image_path) as image:
            exifdata = image.getexif()
            if not exifdata:
                return {}

            relevant_data = {}
            for tag_id, value in exifdata.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag in ['Make', 'Model', 'DateTime', 'DateTimeOriginal', 'Software']:
                    relevant_data[tag] = str(value)

            return relevant_data
    except Exception:
        return {}

def scan_images_directory(directory):
    """Escanea un directorio en busca de imágenes"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    images = []

    if os.path.isdir(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    images.append(os.path.join(root, file))

    return sorted(images)

def test_single_image(image_path):
    """Prueba una sola imagen"""
    print(f"\n[IMAGEN] {os.path.basename(image_path)}")
    print(f"   Ruta: {image_path}")

    # Verificar tamaño del archivo
    try:
        file_size = os.path.getsize(image_path) / 1024  # KB
        print(f"   Tamaño: {file_size:.1f} KB")
    except:
        print("   Tamaño: No disponible")

    # Probar extracción GPS
    gps_data, status = extract_gps_from_image(image_path)

    if gps_data:
        print(f"   [GPS OK] {gps_data['coordinates']}")
        print(f"       Lat: {gps_data['latitude']:.6f}")
        print(f"       Lon: {gps_data['longitude']:.6f}")
    else:
        print(f"   [GPS NO] {status}")

    # Mostrar otra metadata
    other_data = get_other_exif_data(image_path)
    if other_data:
        print("   [METADATA] Adicional:")
        for key, value in other_data.items():
            print(f"       {key}: {value}")
    else:
        print("   [METADATA] Sin metadata adicional")

    return gps_data is not None

def main():
    """Función principal"""
    print_section_header("TEST DE GEOLOCALIZACIÓN EN IMÁGENES")

    # Directorios a escanear
    project_root = Path(__file__).parent.parent
    scan_directories = [
        project_root / "data" / "images" / "train",
        project_root / "data" / "images" / "val",
        project_root / "data" / "images" / "test",
        project_root / "test_images"
    ]

    all_images = []

    # Recopilar todas las imágenes
    for directory in scan_directories:
        if directory.exists():
            images = scan_images_directory(str(directory))
            if images:
                print(f"\nEncontradas {len(images)} imagenes en: {directory}")
                all_images.extend(images)
        else:
            print(f"\nDirectorio no existe: {directory}")

    if not all_images:
        print("\n[ERROR] No se encontraron imagenes para probar")
        return

    print(f"\n[ANALIZANDO] {len(all_images)} IMAGENES TOTALES...")
    print("=" * 60)

    # Estadísticas
    with_gps = 0
    without_gps = 0

    # Probar cada imagen
    for image_path in all_images:
        has_gps = test_single_image(image_path)
        if has_gps:
            with_gps += 1
        else:
            without_gps += 1

    # Resumen final
    print("\n" + "=" * 60)
    print_section_header("RESUMEN DE RESULTADOS")
    print(f"[TOTAL] Imagenes analizadas: {len(all_images)}")
    print(f"[GPS OK] Con geolocalizacion: {with_gps} ({with_gps/len(all_images)*100:.1f}%)")
    print(f"[GPS NO] Sin geolocalizacion: {without_gps} ({without_gps/len(all_images)*100:.1f}%)")

    if with_gps > 0:
        print(f"\n[INFO] {with_gps} imagenes tienen datos GPS que pueden usarse para geolocalizacion")
    else:
        print(f"\n[AVISO] Ninguna imagen tiene datos GPS - considera:")
        print("   - Usar imagenes capturadas con GPS activado")
        print("   - Verificar configuracion de camara/telefono")
        print("   - Obtener imagenes de fuentes que preserven metadata")

if __name__ == "__main__":
    main()