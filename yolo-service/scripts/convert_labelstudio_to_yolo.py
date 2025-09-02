#!/usr/bin/env python3
"""
Convierte anotaciones de LabelStudio a formato YOLO
"""
import json
import os
from pathlib import Path
import argparse

import sys
sys.path.append('..')
from configs.classes import CLASS_NAME_TO_ID as CLASS_MAPPING

def convert_labelstudio_to_yolo(json_file, output_dir):
    """Convierte anotaciones de LabelStudio a formato YOLO"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for item in data:
        # Obtener nombre del archivo
        image_name = Path(item['data']['image']).stem
        
        # Crear archivo de etiquetas
        label_file = output_path / f"{image_name}.txt"
        
        with open(label_file, 'w') as f:
            for annotation in item.get('annotations', []):
                for result in annotation.get('result', []):
                    if result['type'] == 'rectanglelabels':
                        # Extraer información
                        label = result['value']['rectanglelabels'][0]
                        class_id = CLASS_MAPPING.get(label, 0)
                        
                        # Convertir coordenadas a formato YOLO
                        x = result['value']['x'] / 100.0  # LabelStudio usa porcentajes
                        y = result['value']['y'] / 100.0
                        width = result['value']['width'] / 100.0
                        height = result['value']['height'] / 100.0
                        
                        # Calcular centro
                        center_x = x + width / 2
                        center_y = y + height / 2
                        
                        # Escribir línea YOLO
                        f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
    
    print(f"Conversión completada. Etiquetas guardadas en: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="Archivo JSON de LabelStudio")
    parser.add_argument("--output", required=True, help="Directorio de salida")
    
    args = parser.parse_args()
    convert_labelstudio_to_yolo(args.json, args.output)