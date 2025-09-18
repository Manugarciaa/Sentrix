#!/usr/bin/env python3
"""
Versión mejorada para leer GPS de imágenes Xiaomi
"""

import os
import sys
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_gps_improved(image_path):
    """Versión mejorada para extraer GPS de diferentes formatos"""
    try:
        with Image.open(image_path) as image:
            exifdata = image.getexif()

            if not exifdata:
                return None, "No EXIF data"

            # Buscar datos GPS
            for tag_id, value in exifdata.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    print(f"   [DEBUG] GPS data type: {type(value)}")
                    print(f"   [DEBUG] GPS data: {value}")

                    # Manejo de diferentes formatos
                    if hasattr(value, 'items'):  # Formato estándar (dict-like)
                        return parse_gps_dict(value)
                    elif isinstance(value, (list, tuple)):  # Formato lista
                        return parse_gps_list(value)
                    elif isinstance(value, int):  # Formato entero (apuntador?)
                        return None, f"GPS data as int: {value}"
                    else:
                        return None, f"Unknown GPS format: {type(value)}"

            return None, "No GPS in EXIF"

    except Exception as e:
        return None, f"Error: {str(e)}"

def parse_gps_dict(gps_info):
    """Para formato estándar dict-like"""
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
            }, "GPS parsed from dict"
    except Exception as e:
        return None, f"Error parsing dict GPS: {e}"

    return None, "Missing lat/lon in dict"

def parse_gps_list(gps_info):
    """Para formato lista (si existe)"""
    # Placeholder para otros formatos
    return None, f"List GPS format not implemented: {gps_info}"

def convert_to_decimal(coords, ref):
    """Convierte coordenadas DMS a decimal"""
    try:
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
        print(f"   [DEBUG] Error converting coordinates: {e}")
        return 0.0

def test_single_xiaomi_image():
    """Prueba una imagen específica de Xiaomi para debug"""
    xiaomi_images = [
        "C:\\Users\\manolo\\Documents\\Sentrix\\yolo-service\\data\\images\\train\\067205de-IMG_20250829_151908.jpg",
        "C:\\Users\\manolo\\Documents\\Sentrix\\yolo-service\\data\\images\\train\\08411b05-IMG_20250829_151910.jpg"
    ]

    for image_path in xiaomi_images:
        if os.path.exists(image_path):
            print(f"\n[DEBUG TEST] {os.path.basename(image_path)}")
            gps_data, status = extract_gps_improved(image_path)
            if gps_data:
                print(f"   [SUCCESS] GPS: {gps_data['coordinates']}")
            else:
                print(f"   [FAILED] {status}")
            break

if __name__ == "__main__":
    test_single_xiaomi_image()