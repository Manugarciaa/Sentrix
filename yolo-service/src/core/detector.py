"""
Detection module for YOLO Dengue Detection
Módulo de detección para criaderos de dengue
"""

import os
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

from configs.classes import DENGUE_CLASSES, RISK_LEVEL_BY_ID
from ..utils import validate_model_file, validate_file_exists, cleanup_unwanted_downloads, extract_image_gps, get_image_camera_info


def detect_breeding_sites(model_path, source, conf_threshold=0.5, include_gps=True, save_processed_image=True, output_dir=None):
    """
    Detecta sitios de cría en imágenes usando modelo entrenado

    Args:
        model_path (str): Ruta al modelo YOLO entrenado
        source (str): Ruta a la imagen o directorio
        conf_threshold (float): Umbral de confianza para detecciones
        include_gps (bool): Incluir información GPS en cada detección
        save_processed_image (bool): Guardar imagen procesada con detecciones marcadas
        output_dir (str): Directorio donde guardar imagen procesada

    Returns:
        dict: Detecciones y ruta de imagen procesada (si se guarda)
    """
    validate_model_file(model_path)
    validate_file_exists(source, "Imagen/directorio")

    try:
        os.environ['YOLO_VERBOSE'] = 'False'
        model = YOLO(model_path)
        results = model(source, conf=conf_threshold, task='segment')

        # Extraer información GPS una sola vez por imagen
        gps_data = None
        camera_info = None
        if include_gps and os.path.isfile(source):  # Solo para imágenes individuales
            gps_data = extract_image_gps(source)
            camera_info = get_image_camera_info(source)

        detections = []
        processed_image_path = None

        # Process each result
        for result in results:
            if result.masks is not None:
                for i, mask in enumerate(result.masks):
                    class_id = int(result.boxes.cls[i])
                    polygon_coords = mask.xy[0].tolist()

                    # Crear detección básica
                    detection = {
                        'class': DENGUE_CLASSES.get(class_id, f"Clase_{class_id}"),
                        'class_id': class_id,
                        'confidence': float(result.boxes.conf[i]),
                        'polygon': polygon_coords,
                        'mask_area': float(mask.data.sum()),
                        'risk_level': RISK_LEVEL_BY_ID.get(class_id, 'BAJO')
                    }

                    # Agregar información GPS si está disponible
                    if include_gps and gps_data:
                        detection['location'] = _create_detection_location(gps_data, camera_info, detection)
                    elif include_gps:
                        detection['location'] = {
                            'has_location': False,
                            'reason': 'No GPS data available in image'
                        }

                    # Agregar metadata de imagen
                    if include_gps:
                        detection['image_metadata'] = {
                            'source_file': os.path.basename(source) if os.path.isfile(source) else 'multiple_files',
                            'detection_timestamp': None,  # Se puede agregar en el futuro
                            'camera_info': camera_info
                        }

                    detections.append(detection)

        # Crear imagen procesada con detecciones marcadas
        if save_processed_image and os.path.isfile(source) and results:
            processed_image_path = _create_processed_image(source, results[0], output_dir)

        return {
            'detections': detections,
            'processed_image_path': processed_image_path,
            'source_path': source,
            'total_detections': len(detections)
        }

    except Exception as e:
        print(f"Error durante la detección: {e}")
        raise
    finally:
        # Limpiar descargas no deseadas
        cleanup_unwanted_downloads()

def _create_detection_location(gps_data, camera_info, detection):
    """
    Crea información de ubicación específica para una detección individual

    Args:
        gps_data (dict): Datos GPS de la imagen
        camera_info (dict): Información de la cámara
        detection (dict): Datos de la detección específica

    Returns:
        dict: Información de ubicación para la detección
    """
    if not gps_data or not gps_data.get('has_gps', False):
        return {
            'has_location': False,
            'reason': 'No GPS coordinates in image EXIF'
        }

    # Crear ubicación específica para esta detección
    coordinates_string = f"{gps_data['latitude']}, {gps_data['longitude']}"
    location = {
        'has_location': True,
        'latitude': gps_data['latitude'],
        'longitude': gps_data['longitude'],
        'coordinates': coordinates_string,
        'altitude_meters': gps_data.get('altitude'),
        'gps_date': gps_data.get('gps_date'),
        'location_source': gps_data['location_source'],

        # Información específica para backend
        'backend_integration': {
            'geo_point': f"POINT({gps_data['longitude']} {gps_data['latitude']})",
            'risk_level': detection['risk_level'],
            'breeding_site_type': detection['class'],
            'confidence_score': detection['confidence'],
            'area_square_pixels': detection['mask_area'],
            'requires_verification': True,
            'detection_id': None,  # Se puede generar UUID en el backend

            # URLs útiles para verificación
            'verification_urls': {
                'google_maps': f"https://maps.google.com/?q={gps_data['latitude']},{gps_data['longitude']}",
                'google_earth': f"https://earth.google.com/web/search/{gps_data['latitude']},{gps_data['longitude']}",
                'coordinates_string': coordinates_string
            }
        }
    }

    return location


def _create_processed_image(source_path, result, output_dir=None):
    """
    Crear imagen procesada con detecciones marcadas en azul

    Args:
        source_path (str): Ruta de la imagen original
        result: Resultado de YOLO con detecciones
        output_dir (str): Directorio de salida (opcional)

    Returns:
        str: Ruta de la imagen procesada generada
    """
    try:
        # Leer imagen original
        image = cv2.imread(source_path)
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {source_path}")

        # Configurar directorio de salida
        if output_dir is None:
            output_dir = Path(source_path).parent / "processed"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        # Configurar nombre de archivo de salida
        base_name = Path(source_path).stem
        output_path = output_dir / f"{base_name}_processed.jpg"

        # Dibujar detecciones si existen
        if result.masks is not None and result.boxes is not None:
            for i, mask in enumerate(result.masks):
                class_id = int(result.boxes.cls[i])
                confidence = float(result.boxes.conf[i])
                class_name = DENGUE_CLASSES.get(class_id, f"Clase_{class_id}")

                # Obtener polígono de la máscara
                polygon = mask.xy[0].astype(np.int32)

                # Definir color azul (BGR format)
                color = (255, 100, 0)  # Azul brillante

                # Dibujar polígono (contorno)
                cv2.polylines(image, [polygon], isClosed=True, color=color, thickness=3)

                # Rellenar polígono con transparencia
                overlay = image.copy()
                cv2.fillPoly(overlay, [polygon], color)
                image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)

                # Agregar etiqueta con nombre de clase y confianza
                if len(polygon) > 0:
                    # Encontrar punto superior del polígono para colocar etiqueta
                    top_point = polygon[polygon[:, 1].argmin()]
                    label = f"{class_name} {confidence:.2f}"

                    # Configurar texto
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.8
                    font_thickness = 2

                    # Obtener tamaño del texto
                    (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)

                    # Dibujar fondo del texto
                    cv2.rectangle(image,
                                (top_point[0] - 5, top_point[1] - text_height - 10),
                                (top_point[0] + text_width + 5, top_point[1] + 5),
                                color, -1)

                    # Dibujar texto
                    cv2.putText(image, label,
                              (top_point[0], top_point[1] - 5),
                              font, font_scale, (255, 255, 255), font_thickness)

        # Guardar imagen procesada
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])

        print(f"Imagen procesada guardada en: {output_path}")
        return str(output_path)

    except Exception as e:
        print(f"Error creando imagen procesada: {e}")
        return None