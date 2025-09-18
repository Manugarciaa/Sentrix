#!/usr/bin/env python3
"""
Test GPS extraction using exifread library
"""

import os
import exifread

def test_with_exifread(image_path):
    """Usa exifread para extraer GPS"""
    print(f"\n[EXIFREAD TEST] {os.path.basename(image_path)}")

    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        # Mostrar todas las etiquetas GPS
        gps_tags = {k: v for k, v in tags.items() if 'GPS' in k}

        if gps_tags:
            print("   [GPS TAGS FOUND]:")
            for key, value in gps_tags.items():
                print(f"       {key}: {value}")

            # Intentar extraer coordenadas
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = convert_exif_coords(tags['GPS GPSLatitude'])
                lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))

                lon = convert_exif_coords(tags['GPS GPSLongitude'])
                lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))

                if lat_ref == 'S':
                    lat = -lat
                if lon_ref == 'W':
                    lon = -lon

                print(f"   [SUCCESS] Coordinates: {lat:.6f},{lon:.6f}")
                return True
            else:
                print("   [NO COORDS] GPS tags exist but no lat/lon")
        else:
            print("   [NO GPS] No GPS tags found")
        return False

    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def convert_exif_coords(coords):
    """Convierte coordenadas EXIF a decimal"""
    try:
        # coords.values es una lista de fracciones [degrees, minutes, seconds]
        values = coords.values
        degrees = float(values[0].num) / float(values[0].den)
        minutes = float(values[1].num) / float(values[1].den)
        seconds = float(values[2].num) / float(values[2].den)
        return degrees + minutes/60 + seconds/3600
    except Exception as e:
        print(f"       [DEBUG] Error converting: {e}")
        return 0.0

def main():
    """Prueba varias imágenes"""
    test_images = [
        "C:\\Users\\manolo\\Documents\\Sentrix\\yolo-service\\data\\images\\train\\067205de-IMG_20250829_151908.jpg",
        "C:\\Users\\manolo\\Documents\\Sentrix\\yolo-service\\data\\images\\train\\08411b05-IMG_20250829_151910.jpg",
        "C:\\Users\\manolo\\Documents\\Sentrix\\yolo-service\\data\\images\\train\\7fb193cb-IMG_20250412_100507.jpg",
        "C:\\Users\\manolo\\Documents\\Sentrix\\yolo-service\\data\\images\\train\\04c22c36-IMG_20250309_120306141.jpg"
    ]

    success_count = 0
    for image_path in test_images:
        if os.path.exists(image_path):
            if test_with_exifread(image_path):
                success_count += 1

    print(f"\n[SUMMARY] GPS found in {success_count}/{len(test_images)} images tested")

if __name__ == "__main__":
    main()