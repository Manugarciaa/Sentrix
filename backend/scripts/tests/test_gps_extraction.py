"""
Script de prueba para verificar extracción de GPS en diferentes formatos
"""
import sys
from pathlib import Path

# Agregar shared al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'shared'))

from sentrix_shared.gps_utils import extract_gps_from_exif, extract_camera_info_from_exif

print("=== TEST DE EXTRACCIÓN DE GPS ===\n")

# Buscar imágenes de prueba
test_dirs = [
    Path(__file__).parent / "uploads",
    Path(__file__).parent / "temp",
    Path(__file__).parent.parent / "test_images",
]

test_files = []
for test_dir in test_dirs:
    if test_dir.exists():
        # Buscar diferentes formatos
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.heic', '*.heif', '*.webp', '*.tiff']:
            test_files.extend(list(test_dir.glob(ext)))
            test_files.extend(list(test_dir.glob(ext.upper())))

if not test_files:
    print("No se encontraron imágenes de prueba")
    print("\nDirectorios buscados:")
    for d in test_dirs:
        print(f"  - {d}")
    print("\nPara probar, coloca imágenes en alguno de estos directorios")
else:
    print(f"Encontradas {len(test_files)} imágenes para probar:\n")

    for img_path in test_files[:10]:  # Limitar a 10 para no saturar
        print(f"\n{'='*60}")
        print(f"Archivo: {img_path.name}")
        print(f"Formato: {img_path.suffix.upper()}")
        print(f"Tamaño: {img_path.stat().st_size / 1024:.1f} KB")
        print('-' * 60)

        # Extraer GPS
        gps_data = extract_gps_from_exif(img_path)

        if gps_data.get('has_gps'):
            print(f"✓ GPS ENCONTRADO:")
            print(f"  Latitud: {gps_data['latitude']:.6f}")
            print(f"  Longitud: {gps_data['longitude']:.6f}")
            if gps_data.get('altitude'):
                print(f"  Altitud: {gps_data['altitude']:.1f} m")
            if gps_data.get('gps_date'):
                print(f"  Fecha GPS: {gps_data['gps_date']}")
            if gps_data.get('gps_timestamp'):
                print(f"  Hora GPS: {gps_data['gps_timestamp']}")
        else:
            print(f"✗ GPS NO ENCONTRADO")
            if 'error' in gps_data:
                print(f"  Error: {gps_data['error']}")

        # Extraer info de cámara
        camera_info = extract_camera_info_from_exif(img_path)

        if not camera_info.get('error'):
            if camera_info.get('camera_make') or camera_info.get('camera_model'):
                print(f"\n📷 CÁMARA:")
                if camera_info.get('camera_make'):
                    print(f"  Marca: {camera_info['camera_make']}")
                if camera_info.get('camera_model'):
                    print(f"  Modelo: {camera_info['camera_model']}")
                if camera_info.get('datetime_original'):
                    print(f"  Fecha: {camera_info['datetime_original']}")

print("\n" + "="*60)
print("TEST COMPLETADO")
print("="*60)

# Resumen
print("\n=== RESUMEN ===")
print(f"Total imágenes analizadas: {min(len(test_files), 10)}")

if test_files:
    # Contar por formato
    formats = {}
    for f in test_files[:10]:
        ext = f.suffix.upper()
        formats[ext] = formats.get(ext, 0) + 1

    print("\nFormatos encontrados:")
    for ext, count in sorted(formats.items()):
        print(f"  {ext}: {count} archivo(s)")

print("\n💡 TIP: Para probar específicamente archivos HEIC:")
print("   1. Coloca imágenes HEIC en backend/uploads/")
print("   2. Ejecuta este script nuevamente")
print("   3. Verifica que el GPS se extraiga correctamente")
