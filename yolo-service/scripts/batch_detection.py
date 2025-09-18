import argparse
import os
import glob
from pathlib import Path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import detect_breeding_sites
from src.reports import generate_report, save_report
from src.utils import validate_model_file, validate_file_exists, get_image_extensions, ensure_directory, get_results_dir
from src.utils.file_ops import print_section_header

def process_image_directory(model_path, images_dir, output_dir, conf_threshold=0.5):
    """Procesa todas las imágenes en un directorio"""
    
    # Usar extensiones desde utils
    image_extensions = get_image_extensions()
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(images_dir, ext)))
        image_files.extend(glob.glob(os.path.join(images_dir, ext.upper())))
    
    if not image_files:
        print(f"No se encontraron imagenes en: {images_dir}")
        return
    
    ensure_directory(output_dir)
    
    print(f"Procesando {len(image_files)} imágenes...")
    
    results_summary = []
    
    for i, image_path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Procesando: {os.path.basename(image_path)}")
        
        try:
            detections = detect_breeding_sites(model_path, image_path, conf_threshold)
            report = generate_report(image_path, detections)
            
            image_name = Path(image_path).stem
            output_path = os.path.join(output_dir, f"{image_name}_report.json")
            save_report(report, output_path)
            
            results_summary.append({
                'image': os.path.basename(image_path),
                'detections': len(detections),
                'risk_level': report['risk_assessment']['level']
            })
            
            print(f"  - Detecciones: {len(detections)}")
            print(f"  - Riesgo: {report['risk_assessment']['level']}")
            
        except Exception as e:
            print(f"  - Error: {e}")
            results_summary.append({
                'image': os.path.basename(image_path),
                'error': str(e)
            })
    
    # Resumen final
    print("\n=== RESUMEN ===")
    total_processed = len([r for r in results_summary if 'error' not in r])
    total_errors = len([r for r in results_summary if 'error' in r])
    
    print(f"Imágenes procesadas: {total_processed}")
    print(f"Errores: {total_errors}")
    
    if total_processed > 0:
        risk_distribution = {}
        total_detections = 0
        
        for result in results_summary:
            if 'error' not in result:
                risk = result['risk_level']
                risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
                total_detections += result['detections']
        
        print(f"Total detecciones: {total_detections}")
        print("Distribución de riesgo:")
        for risk, count in risk_distribution.items():
            print(f"  - {risk}: {count} imágenes")

def main():
    parser = argparse.ArgumentParser(description='Procesamiento en lote de imágenes para detección de criaderos')
    parser.add_argument('--model', type=str, required=True,
                        help='Ruta al modelo entrenado (.pt)')
    parser.add_argument('--images', type=str, required=True,
                        help='Directorio con imágenes a procesar')
    parser.add_argument('--output', type=str, default='results/batch_results',
                        help='Directorio de salida para reportes')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='Umbral de confianza (0-1)')
    
    args = parser.parse_args()
    
    # Validar usando funciones utilitarias
    try:
        validate_model_file(args.model)
        validate_file_exists(args.images, "Directorio de imagenes")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print_section_header("PROCESAMIENTO EN LOTE")
    print(f"Modelo: {args.model}")
    print(f"Directorio de imágenes: {args.images}")
    print(f"Directorio de salida: {args.output}")
    print(f"Umbral de confianza: {args.conf}")
    print()
    
    process_image_directory(args.model, args.images, args.output, args.conf)

if __name__ == "__main__":
    main()