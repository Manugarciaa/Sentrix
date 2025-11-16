import os
import requests
from pathlib import Path
import base64
import shutil

# Configuración
YOLO_SERVICE_URL = "http://localhost:8001/detect"
TEST_IMAGES_DIR = Path("test_images")
OUTPUT_DIR = Path("../docs/imagenes/ejemplos_yolo")

# Crear directorio de salida
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Buscar imágenes disponibles en test_images
imagenes_disponibles = list(TEST_IMAGES_DIR.glob("*.jpg")) + list(TEST_IMAGES_DIR.glob("*.png")) + list(TEST_IMAGES_DIR.glob("*.jpeg"))

print("=" * 60)
print("GENERANDO EJEMPLOS DE DETECCIONES PARA LA TESIS")
print("=" * 60)
print(f"\nImágenes disponibles en test_images/: {len(imagenes_disponibles)}")

if len(imagenes_disponibles) < 4:
    print("\n[WARNING] Se necesitan al menos 4 imagenes en test_images/")
    print("   Puedes usar las mismas imagenes varias veces si es necesario")

# Tomar las primeras 4 imágenes (o las que haya)
imagenes = imagenes_disponibles[:4] if len(imagenes_disponibles) >= 4 else imagenes_disponibles

casos = ['a', 'b', 'c', 'd']

for i, imagen_path in enumerate(imagenes):
    caso = casos[i] if i < len(casos) else chr(97 + i)

    print(f"\n[{i+1}/{len(imagenes)}] Procesando: {imagen_path.name}")
    print(f"   Caso: ({caso})")

    # Enviar imagen al YOLO Service
    with open(imagen_path, 'rb') as f:
        files = {'file': (imagen_path.name, f, 'image/jpeg')}
        data = {'confidence_threshold': 0.5}

        try:
            response = requests.post(YOLO_SERVICE_URL, files=files, data=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                num_detecciones = len(result.get('detections', []))

                # Guardar imagen procesada
                if 'processed_image_base64' in result:
                    img_data = result['processed_image_base64']

                    # Remover prefijo data:image si existe
                    if 'base64,' in img_data:
                        img_data = img_data.split('base64,')[1]

                    img_bytes = base64.b64decode(img_data)

                    # Guardar imagen procesada
                    output_path = OUTPUT_DIR / f"caso_{caso}_procesada.jpg"
                    with open(output_path, 'wb') as out:
                        out.write(img_bytes)

                    print(f"   [OK] Procesada guardada: {output_path.name}")
                    print(f"   Detecciones: {num_detecciones}")

                    # Copiar imagen original
                    original_output = OUTPUT_DIR / f"caso_{caso}_original.jpg"
                    shutil.copy(imagen_path, original_output)
                    print(f"   [OK] Original guardada: {original_output.name}")

                else:
                    print(f"   [WARNING] No se genero imagen procesada")
            else:
                print(f"   [ERROR] HTTP {response.status_code}: {response.text[:100]}")

        except requests.exceptions.Timeout:
            print(f"   [ERROR] Timeout - El servicio YOLO tardo demasiado")
        except Exception as e:
            print(f"   [ERROR] {e}")

print("\n" + "=" * 60)
print("PROCESO COMPLETADO!")
print(f"\nImagenes guardadas en:")
print(f"   {OUTPUT_DIR.absolute()}")
print("\nArchivos generados:")

# Listar archivos generados
archivos = sorted(OUTPUT_DIR.glob("*.jpg"))
for archivo in archivos:
    print(f"   - {archivo.name}")

print("\nSiguiente paso: Crear grid 2x2 con estas imagenes")
print("=" * 60)
