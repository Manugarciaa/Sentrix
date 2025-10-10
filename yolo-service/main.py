"""
Main entry point for YOLO Dengue Detection Service
Punto de entrada principal para el Servicio de Detección de Criaderos de Dengue

Usage examples:
    # Train model
    python main.py train --model yolo11n-seg.pt --epochs 100

    # Detect in image
    python main.py detect --model models/best.pt --source image.jpg

    # Generate report
    python main.py report --model models/best.pt --source image.jpg --output results/
"""

import argparse
import sys
import os

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import train_dengue_model, detect_breeding_sites, assess_dengue_risk
from src.reports import generate_report, save_report
from src.utils import detect_device, validate_file_exists, get_default_dataset_config
from src.utils.file_ops import print_section_header


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='YOLO Dengue Detection Service - Detección de criaderos de dengue'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Train command
    train_parser = subparsers.add_parser('train', help='Train dengue detection model')
    train_parser.add_argument('--model', default='yolo11n-seg.pt', help='Model path')
    train_parser.add_argument('--data', default=None, help='Dataset config (default: configs/dataset.yaml)')
    train_parser.add_argument('--epochs', type=int, default=100, help='Training epochs')
    train_parser.add_argument('--name', help='Experiment name')

    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Detect breeding sites')
    detect_parser.add_argument('--model', required=True, help='Trained model path')
    detect_parser.add_argument('--source', required=True, help='Image or directory path')
    detect_parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold')
    detect_parser.add_argument('--no-gps', action='store_true', help='Disable GPS metadata extraction')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate detection report')
    report_parser.add_argument('--model', required=True, help='Trained model path')
    report_parser.add_argument('--source', required=True, help='Image path')
    report_parser.add_argument('--output', default='results/detection_report.json', help='Output path')
    report_parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold')
    report_parser.add_argument('--no-gps', action='store_true', help='Disable GPS metadata extraction')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'train':
            print_section_header("ENTRENAMIENTO YOLO DENGUE")
            # Usar configuración por defecto si no se especifica
            data_config = args.data if args.data else str(get_default_dataset_config())

            results = train_dengue_model(
                model_path=args.model,
                data_config=data_config,
                epochs=args.epochs,
                experiment_name=args.name
            )
            print("[OK] Entrenamiento completado exitosamente")

        elif args.command == 'detect':
            print_section_header("DETECCIÓN DE CRIADEROS")
            include_gps = not args.no_gps
            result = detect_breeding_sites(
                model_path=args.model,
                source=args.source,
                conf_threshold=args.conf,
                include_gps=include_gps
            )
            detections = result['detections']
            print(f"[OK] Detecciones encontradas: {len(detections)}")
            if result.get('processed_image_path'):
                print(f"[OK] Imagen procesada: {result['processed_image_path']}")
            for detection in detections:
                gps_info = ""
                if include_gps and detection.get('location', {}).get('has_location', False):
                    coords = detection['location']['coordinates']
                    gps_info = f" [GPS: {coords}]"
                print(f"  - {detection['class']}: {detection['confidence']:.2f}{gps_info}")

        elif args.command == 'report':
            print_section_header("GENERACIÓN DE REPORTE")
            include_gps = not args.no_gps
            result = detect_breeding_sites(
                model_path=args.model,
                source=args.source,
                conf_threshold=args.conf,
                include_gps=include_gps
            )
            detections = result['detections']
            report = generate_report(args.source, detections, include_gps=include_gps)
            save_report(report, args.output)

            print(f"[OK] Reporte generado: {args.output}")
            print(f"  Detecciones: {report['total_detections']}")
            print(f"  Nivel de riesgo: {report['risk_assessment']['level']}")
            if include_gps and any(d.get('location', {}).get('has_location', False) for d in detections):
                gps_detections = sum(1 for d in detections if d.get('location', {}).get('has_location', False))
                print(f"  Detecciones con GPS: {gps_detections}/{len(detections)}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()