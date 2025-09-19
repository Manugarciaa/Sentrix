"""
Main entry point for Sentrix Backend Service
Punto de entrada principal para el Servicio Backend de Sentrix

Usage examples:
    # Database management
    python main.py db status
    python main.py db migrate

    # Image analysis
    python main.py analyze --image image.jpg --user-id 1
    python main.py batch --directory images/ --user-id 1

    # Expert validation
    python main.py validate list --priority high_risk
    python main.py validate approve --detection-id 123 --expert-id 5
"""

import argparse
import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import SentrixAPIManager, AnalysisProcessor, DetectionValidator
from src.database.connection import test_connection, get_database_info
from src.utils import get_project_root, validate_connection
from src.schemas.analyses import AnalysisCreate


def print_section_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Sentrix Backend Service - Gestión de análisis epidemiológicos'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Database commands
    db_parser = subparsers.add_parser('db', help='Database management')
    db_subparsers = db_parser.add_subparsers(dest='db_action', help='Database actions')

    status_parser = db_subparsers.add_parser('status', help='Check database status')
    migrate_parser = db_subparsers.add_parser('migrate', help='Run database migrations')
    seed_parser = db_subparsers.add_parser('seed', help='Seed database with sample data')
    seed_parser.add_argument('--sample-data', action='store_true', help='Include sample data')

    # Analysis commands
    analyze_parser = subparsers.add_parser('analyze', help='Analyze single image')
    analyze_parser.add_argument('--image', required=True, help='Image path')
    analyze_parser.add_argument('--user-id', type=int, required=True, help='User ID')
    analyze_parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold')
    analyze_parser.add_argument('--no-gps', action='store_true', help='Disable GPS metadata extraction')

    batch_parser = subparsers.add_parser('batch', help='Batch process images')
    batch_parser.add_argument('--directory', required=True, help='Images directory')
    batch_parser.add_argument('--user-id', type=int, required=True, help='User ID')
    batch_parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold')
    batch_parser.add_argument('--no-gps', action='store_true', help='Disable GPS metadata extraction')

    # Validation commands
    validate_parser = subparsers.add_parser('validate', help='Expert validation')
    validate_subparsers = validate_parser.add_subparsers(dest='validate_action', help='Validation actions')

    list_parser = validate_subparsers.add_parser('list', help='List pending validations')
    list_parser.add_argument('--priority', choices=['high_risk', 'high_confidence', 'all'],
                           default='high_risk', help='Priority filter')
    list_parser.add_argument('--limit', type=int, default=50, help='Limit results')

    approve_parser = validate_subparsers.add_parser('approve', help='Approve detection')
    approve_parser.add_argument('--detection-id', type=int, required=True, help='Detection ID')
    approve_parser.add_argument('--expert-id', type=int, required=True, help='Expert ID')
    approve_parser.add_argument('--notes', help='Expert notes')

    reject_parser = validate_subparsers.add_parser('reject', help='Reject detection')
    reject_parser.add_argument('--detection-id', type=int, required=True, help='Detection ID')
    reject_parser.add_argument('--expert-id', type=int, required=True, help='Expert ID')
    reject_parser.add_argument('--notes', help='Expert notes')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'db':
            await handle_database_commands(args)
        elif args.command == 'analyze':
            await handle_analyze_command(args)
        elif args.command == 'batch':
            await handle_batch_command(args)
        elif args.command == 'validate':
            await handle_validate_commands(args)

    except Exception as e:
        print(f"ERROR: Error: {e}")
        sys.exit(1)


async def handle_database_commands(args):
    """Handle database management commands"""
    if args.db_action == 'status':
        print_section_header("ESTADO DE LA BASE DE DATOS")

        # Test basic connection
        connection_ok = test_connection()
        print(f"Conexión básica: {'✓' if connection_ok else 'ERROR:'}")

        if connection_ok:
            # Get detailed info
            db_info = get_database_info()
            print(f"URL: {db_info.get('database_url', 'N/A')}")
            print(f"Versión: {db_info.get('version', 'N/A')}")
            print(f"PostGIS disponible: {'✓' if db_info.get('postgis_available') else 'ERROR:'}")

        # Test utils validation
        utils_validation = validate_connection()
        print(f"Validación utils: {'✓' if utils_validation else 'ERROR:'}")

    elif args.db_action == 'migrate':
        print_section_header("EJECUTANDO MIGRACIONES")
        # Import here to avoid circular imports
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("configs/alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✓ Migraciones ejecutadas exitosamente")

    elif args.db_action == 'seed':
        print_section_header("CREANDO DATOS DE PRUEBA")
        await create_sample_data(include_sample=args.sample_data)
        print("✓ Datos de prueba creados exitosamente")


async def handle_analyze_command(args):
    """Handle single image analysis"""
    print_section_header("ANÁLISIS DE IMAGEN")

    # Validate image exists
    if not Path(args.image).exists():
        raise FileNotFoundError(f"Image not found: {args.image}")

    # Create analysis
    api_manager = SentrixAPIManager()
    analysis_data = AnalysisCreate(
        image_path=args.image,
        user_id=args.user_id,
        confidence_threshold=args.confidence
    )

    print(f"Procesando imagen: {args.image}")
    print(f"Usuario: {args.user_id}")
    print(f"Umbral de confianza: {args.confidence}")

    result = await api_manager.create_analysis(analysis_data)

    print(f"✓ Análisis completado")
    print(f"  ID del análisis: {result.id}")
    print(f"  Detecciones encontradas: {result.total_detections}")
    print(f"  Nivel de riesgo: {result.risk_level}")


async def handle_batch_command(args):
    """Handle batch image processing"""
    print_section_header("PROCESAMIENTO POR LOTES")

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {args.directory}")

    # Find images
    image_extensions = ['.jpg', '.jpeg', '.png', '.tiff']
    image_paths = [
        str(img) for img in directory.iterdir()
        if img.suffix.lower() in image_extensions
    ]

    if not image_paths:
        print(f"ERROR: No se encontraron imágenes en: {args.directory}")
        return

    print(f"Encontradas {len(image_paths)} imágenes")
    print(f"Usuario: {args.user_id}")
    print(f"Incluir GPS: {not args.no_gps}")

    # Process batch
    processor = AnalysisProcessor()
    results = await processor.batch_process_images(
        image_paths=image_paths,
        user_id=args.user_id,
        confidence_threshold=args.confidence,
        include_gps=not args.no_gps
    )

    print(f"✓ Procesamiento por lotes completado")
    print(f"  Imágenes procesadas: {results['processed']}")
    print(f"  Imágenes fallidas: {results['failed']}")
    print(f"  Total de análisis: {len(results['analyses'])}")

    if results['errors']:
        print("ERROR: Errores encontrados:")
        for error in results['errors']:
            print(f"  - {error['image_path']}: {error['error']}")


async def handle_validate_commands(args):
    """Handle expert validation commands"""
    validator = DetectionValidator()

    if args.validate_action == 'list':
        print_section_header("DETECCIONES PENDIENTES DE VALIDACIÓN")

        pending = validator.get_pending_validations(
            priority=args.priority,
            limit=args.limit
        )

        if not pending:
            print("No hay detecciones pendientes")
            return

        print(f"Encontradas {len(pending)} detecciones pendientes:")
        for detection in pending:
            gps_icon = "LOCATION:" if detection['has_gps'] else "📷"
            print(f"  {gps_icon} ID: {detection['detection_id']} | "
                  f"Clase: {detection['class_name']} | "
                  f"Confianza: {detection['confidence']:.2f} | "
                  f"Riesgo: {detection['risk_level']}")

    elif args.validate_action in ['approve', 'reject']:
        is_valid = args.validate_action == 'approve'
        action_text = "APROBACIÓN" if is_valid else "RECHAZO"

        print_section_header(f"{action_text} DE DETECCIÓN")

        result = validator.validate_detection(
            detection_id=args.detection_id,
            expert_id=args.expert_id,
            is_valid=is_valid,
            expert_notes=args.notes
        )

        status_icon = "✓" if is_valid else "ERROR:"
        print(f"{status_icon} Detección {args.detection_id} {action_text.lower()} por experto {args.expert_id}")
        if args.notes:
            print(f"  Notas: {args.notes}")


async def create_sample_data(include_sample: bool = False):
    """Create sample data for testing"""
    if not include_sample:
        print("Creación de datos de muestra saltada (usar --sample-data para incluir)")
        return

    from src.database.models import User, Analysis, Detection
    from src.utils.database_utils import get_db_context

    with get_db_context() as db:
        # Create sample user if not exists
        sample_user = db.query(User).filter(User.email == "test@sentrix.com").first()
        if not sample_user:
            sample_user = User(
                email="test@sentrix.com",
                full_name="Test User",
                role="user"
            )
            db.add(sample_user)
            db.flush()

        print(f"Usuario de prueba creado: {sample_user.email} (ID: {sample_user.id})")


if __name__ == "__main__":
    asyncio.run(main())