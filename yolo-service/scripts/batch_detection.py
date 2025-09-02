#!/usr/bin/env python3
"""
Script para procesamiento en lote de detección de focos de dengue
"""
import os
import sys
import json
from pathlib import Path
sys.path.append('..')

from main import detect_breeding_sites, DENGUE_CLASSES

def batch_detect_images(model_path, images_dir, output_dir='results/batch_detection'):
    """
    Procesa múltiples imágenes para detección de focos de dengue
    """
    images_path = Path(images_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    all_results = []
    total_images = 0
    total_detections = 0
    
    print(f"Processing images from: {images_dir}")
    print(f"Using model: {model_path}")
    print("-" * 50)
    
    for image_file in images_path.glob('*'):
        if image_file.suffix.lower() in image_extensions:
            total_images += 1
            print(f"Processing: {image_file.name}")
            
            try:
                results, detections = detect_breeding_sites(
                    model_path=model_path,
                    source=str(image_file),
                    save_results=False
                )
                
                total_detections += len(detections)
                
                image_result = {
                    'image': image_file.name,
                    'detections_count': len(detections),
                    'detections': detections
                }
                all_results.append(image_result)
                
                print(f"  Found {len(detections)} potential breeding sites")
                
            except Exception as e:
                print(f"  Error processing {image_file.name}: {e}")
    
    # Save batch results
    batch_report = {
        'summary': {
            'total_images': total_images,
            'total_detections': total_detections,
            'model_used': model_path,
            'images_directory': str(images_dir)
        },
        'results': all_results
    }
    
    report_file = output_path / 'batch_detection_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(batch_report, f, indent=2, ensure_ascii=False)
    
    print("-" * 50)
    print(f"Batch processing complete!")
    print(f"Total images processed: {total_images}")
    print(f"Total detections found: {total_detections}")
    print(f"Report saved to: {report_file}")
    
    return batch_report

def generate_summary_report(batch_report):
    """
    Genera un reporte resumen de las detecciones
    """
    class_counts = {}
    high_risk_images = []
    
    for result in batch_report['results']:
        for detection in result['detections']:
            class_name = detection['class']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # Check for high-risk images  
        from configs.classes import HIGH_RISK_CLASSES
        high_risk_count = sum(1 for d in result['detections'] 
                             if d['class'] in HIGH_RISK_CLASSES)
        
        if high_risk_count >= 2:
            high_risk_images.append({
                'image': result['image'],
                'high_risk_sites': high_risk_count,
                'total_sites': result['detections_count']
            })
    
    print("\n=== REPORTE RESUMEN ===")
    print("Tipos de focos detectados:")
    for class_name, count in sorted(class_counts.items()):
        print(f"  {class_name}: {count}")
    
    print(f"\nImágenes de alto riesgo: {len(high_risk_images)}")
    for img in high_risk_images:
        print(f"  {img['image']}: {img['high_risk_sites']} focos de alto riesgo")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch detection of dengue breeding sites")
    parser.add_argument("--model", required=True, help="Path to trained model")
    parser.add_argument("--images", required=True, help="Directory with images to process")
    parser.add_argument("--output", default="results/batch_detection", help="Output directory")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        sys.exit(1)
    
    if not os.path.exists(args.images):
        print(f"Error: Images directory not found: {args.images}")
        sys.exit(1)
    
    batch_report = batch_detect_images(args.model, args.images, args.output)
    generate_summary_report(batch_report)