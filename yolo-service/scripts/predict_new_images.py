#!/usr/bin/env python3
"""
Script para probar el modelo entrenado con imágenes nuevas
"""
import argparse
import os
import sys
import cv2
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ultralytics import YOLO
from configs.classes import DENGUE_CLASSES
from src.utils import ensure_directory, detect_device

def load_model(model_path):
    """Carga el modelo entrenado"""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modelo no encontrado: {model_path}")

    print(f"Cargando modelo: {model_path}")
    model = YOLO(model_path)
    return model

def process_single_image(model, image_path, output_dir, conf_threshold=0.25):
    """Procesa una sola imagen y guarda resultados"""
    print(f"Procesando: {os.path.basename(image_path)}")

    # Realizar predicción
    results = model.predict(
        source=image_path,
        conf=conf_threshold,
        save=False,
        verbose=False
    )

    # Procesar resultados
    result = results[0]
    detections = []

    if result.boxes is not None and len(result.boxes) > 0:
        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()

        for i, (box, conf, cls) in enumerate(zip(boxes, confs, classes)):
            class_name = DENGUE_CLASSES[int(cls)]
            detection = {
                'class': class_name,
                'confidence': float(conf),
                'bbox': {
                    'x1': float(box[0]),
                    'y1': float(box[1]),
                    'x2': float(box[2]),
                    'y2': float(box[3])
                }
            }
            detections.append(detection)

    # Guardar imagen con detecciones
    image_name = Path(image_path).stem
    output_image_path = os.path.join(output_dir, f"{image_name}_predicted.jpg")

    # Usar el método plot de ultralytics para dibujar
    annotated_img = result.plot()
    cv2.imwrite(output_image_path, annotated_img)

    # Guardar JSON con detecciones
    output_json_path = os.path.join(output_dir, f"{image_name}_detections.json")
    detection_data = {
        'image': os.path.basename(image_path),
        'timestamp': datetime.now().isoformat(),
        'model_confidence_threshold': conf_threshold,
        'total_detections': len(detections),
        'detections': detections,
        'risk_assessment': assess_risk(detections)
    }

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(detection_data, f, indent=2, ensure_ascii=False)

    return detections, output_image_path, output_json_path

def assess_risk(detections):
    """Evalúa el riesgo epidemiológico basado en detecciones"""
    high_risk_classes = ['Charcos/Cumulo de agua', 'Huecos']
    medium_risk_classes = ['Basura']

    high_risk_count = sum(1 for d in detections if d['class'] in high_risk_classes)
    medium_risk_count = sum(1 for d in detections if d['class'] in medium_risk_classes)

    if high_risk_count >= 2:
        risk_level = "ALTO"
        priority = "INMEDIATA"
        recommendations = [
            "Intervención urgente requerida",
            "Eliminar agua estancada inmediatamente",
            "Contactar servicios de salud"
        ]
    elif high_risk_count >= 1:
        risk_level = "MEDIO-ALTO"
        priority = "24-48 HORAS"
        recommendations = [
            "Eliminar fuentes de agua estancada",
            "Monitoreo frecuente necesario"
        ]
    elif medium_risk_count >= 3:
        risk_level = "MEDIO"
        priority = "1 SEMANA"
        recommendations = [
            "Limpiar basura acumulada",
            "Mejorar manejo de residuos"
        ]
    elif medium_risk_count >= 1:
        risk_level = "BAJO"
        priority = "2 SEMANAS"
        recommendations = [
            "Mantenimiento preventivo",
            "Limpieza regular del área"
        ]
    else:
        risk_level = "MÍNIMO"
        priority = "RUTINA"
        recommendations = ["Vigilancia rutinaria"]

    return {
        'level': risk_level,
        'priority': priority,
        'high_risk_sites': high_risk_count,
        'medium_risk_sites': medium_risk_count,
        'recommendations': recommendations
    }

def process_images(model_path, input_path, output_dir="predictions", conf_threshold=0.25):
    """Procesa una imagen o directorio de imágenes"""

    # Crear directorio de salida
    ensure_directory(output_dir)

    # Cargar modelo
    model = load_model(model_path)

    # Determinar si es archivo o directorio
    if os.path.isfile(input_path):
        image_files = [input_path]
    elif os.path.isdir(input_path):
        # Buscar imágenes en el directorio
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
        image_files = []
        for ext in extensions:
            image_files.extend(Path(input_path).glob(f'*{ext}'))
            image_files.extend(Path(input_path).glob(f'*{ext.upper()}'))
        image_files = [str(f) for f in image_files]
    else:
        raise ValueError(f"Ruta no válida: {input_path}")

    if not image_files:
        print("No se encontraron imágenes para procesar")
        return

    print(f"Encontradas {len(image_files)} imágenes para procesar")
    print(f"Umbral de confianza: {conf_threshold}")
    print(f"Directorio de salida: {output_dir}")
    print("-" * 50)

    # Procesar cada imagen
    total_detections = 0
    high_risk_images = 0

    for i, image_path in enumerate(image_files, 1):
        try:
            detections, pred_path, json_path = process_single_image(
                model, image_path, output_dir, conf_threshold
            )

            total_detections += len(detections)

            # Evaluar riesgo
            risk_data = assess_risk(detections)
            if risk_data['level'] in ['ALTO', 'MEDIO-ALTO']:
                high_risk_images += 1
                print(f"  [WARN]  RIESGO {risk_data['level']} - {len(detections)} detecciones")
            else:
                print(f"  [OK] Riesgo {risk_data['level']} - {len(detections)} detecciones")

            print(f"     Imagen guardada: {os.path.basename(pred_path)}")
            print(f"     JSON guardado: {os.path.basename(json_path)}")

        except Exception as e:
            print(f"  [ERROR] Error procesando {os.path.basename(image_path)}: {e}")

        print()

    # Resumen final
    print("=" * 50)
    print("RESUMEN DE PROCESAMIENTO")
    print(f"Imágenes procesadas: {len(image_files)}")
    print(f"Total de detecciones: {total_detections}")
    print(f"Imágenes de alto riesgo: {high_risk_images}")
    print(f"Resultados guardados en: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Predice criaderos de dengue en imágenes nuevas')
    parser.add_argument('--model', required=True,
                       help='Ruta al modelo entrenado (.pt)')
    parser.add_argument('--source', required=True,
                       help='Imagen o directorio de imágenes a procesar')
    parser.add_argument('--output', default='predictions',
                       help='Directorio de salida (default: predictions)')
    parser.add_argument('--conf', type=float, default=0.25,
                       help='Umbral de confianza (default: 0.25)')

    args = parser.parse_args()

    # Mostrar información del sistema
    device = detect_device()
    print("PREDICCIÓN DE CRIADEROS DE DENGUE")
    print("=" * 50)
    print(f"Dispositivo: {device}")
    print(f"Modelo: {args.model}")
    print(f"Fuente: {args.source}")
    print()

    process_images(args.model, args.source, args.output, args.conf)

if __name__ == "__main__":
    main()