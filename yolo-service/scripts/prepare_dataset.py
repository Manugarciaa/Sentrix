#!/usr/bin/env python3
"""
Script para preparar y organizar el dataset de focos de dengue
"""
import os
import shutil
from pathlib import Path
import argparse

def prepare_dengue_dataset(source_dir, target_dir):
    """
    Organiza las imágenes y etiquetas en la estructura requerida por YOLOv11
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create directory structure
    for split in ['train', 'val', 'test']:
        (target_path / 'images' / split).mkdir(parents=True, exist_ok=True)
        (target_path / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    print(f"Dataset structure created in {target_dir}")
    print("Copy your images and labels to the appropriate folders:")
    print("- Images: data/images/train/, data/images/val/, data/images/test/")
    print("- Labels: data/labels/train/, data/labels/val/, data/labels/test/")

def validate_annotations(labels_dir):
    """
    Valida que las anotaciones estén en el formato correcto
    """
    labels_path = Path(labels_dir)
    valid_classes = set(range(4))  # 0-3 classes
    
    for label_file in labels_path.glob('**/*.txt'):
        with open(label_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split()
                if not parts:
                    continue
                    
                try:
                    class_id = int(parts[0])
                    if class_id not in valid_classes:
                        print(f"Warning: Invalid class {class_id} in {label_file}:{line_num}")
                    
                    # Validate bounding box coordinates
                    coords = [float(x) for x in parts[1:5]]
                    for coord in coords:
                        if not 0 <= coord <= 1:
                            print(f"Warning: Coordinate out of range in {label_file}:{line_num}")
                            
                except (ValueError, IndexError):
                    print(f"Error: Invalid format in {label_file}:{line_num}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare dengue detection dataset")
    parser.add_argument("--source", help="Source directory with raw data")
    parser.add_argument("--target", default="data", help="Target directory for organized data")
    parser.add_argument("--validate", action="store_true", help="Validate annotations")
    
    args = parser.parse_args()
    
    if args.source:
        prepare_dengue_dataset(args.source, args.target)
    
    if args.validate:
        validate_annotations(os.path.join(args.target, 'labels'))