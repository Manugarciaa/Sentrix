#!/usr/bin/env python3
"""
Main entry point for Sentrix Backend Service
Punto de entrada principal para el Servicio Backend de Sentrix

Usage:
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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import SentrixAPIManager, AnalysisProcessor, DetectionValidator
from src.database.connection import test_connection, get_database_info
from src.utils import get_project_root, validate_connection
from src.schemas.analyses import AnalysisCreate
from shared.data_models import UserRoleEnum


def print_section_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


async def handle_database_commands(args):
    """Handle database-related commands"""
    print_section_header("DATABASE MANAGEMENT")

    if args.db_action == "status":
        print("🔍 Checking database connection...")

        if test_connection():
            print("✅ Database connection: OK")

            db_info = get_database_info()
            print(f"📊 Database URL: {db_info.get('database_url', 'Unknown')}")
            print(f"🔧 Version: {db_info.get('version', 'Unknown')}")
            print(f"🌍 PostGIS: {'✅ Available' if db_info.get('postgis_available') else '❌ Not available'}")
        else:
            print("❌ Database connection: FAILED")
            return False

    elif args.db_action == "migrate":
        print("🔄 Running database migrations...")
        try:
            from src.database.migrations import run_migrations
            success = run_migrations()
            if success:
                print("✅ Migrations completed successfully")
            else:
                print("❌ Migrations failed")
                return False
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False

    elif args.db_action == "info":
        print("📊 Database Information:")
        db_info = get_database_info()
        for key, value in db_info.items():
            print(f"   {key}: {value}")

    return True


async def handle_analysis_commands(args):
    """Handle analysis-related commands"""
    print_section_header("IMAGE ANALYSIS")

    processor = AnalysisProcessor()

    if args.image:
        print(f"🖼️  Analyzing image: {args.image}")

        # Create analysis request
        analysis_request = AnalysisCreate(
            image_filename=args.image,
            confidence_threshold=getattr(args, 'confidence', 0.5),
            user_id=args.user_id if hasattr(args, 'user_id') else None
        )

        try:
            result = await processor.process_single_analysis(analysis_request)

            print(f"✅ Analysis completed: {result.get('analysis_id')}")
            print(f"📍 GPS Data: {'Yes' if result.get('has_gps_data') else 'No'}")
            print(f"🔍 Detections: {result.get('total_detections', 0)}")
            print(f"⚠️  Risk Level: {result.get('risk_level', 'Unknown')}")

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False

    elif args.directory:
        print(f"📁 Batch analyzing directory: {args.directory}")

        try:
            results = await processor.process_batch_analysis(
                directory_path=args.directory,
                user_id=getattr(args, 'user_id', None),
                confidence_threshold=getattr(args, 'confidence', 0.5)
            )

            print(f"✅ Batch analysis completed")
            print(f"📊 Total processed: {len(results)}")
            successful = sum(1 for r in results if r.get('status') == 'completed')
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {len(results) - successful}")

        except Exception as e:
            print(f"❌ Batch analysis failed: {e}")
            return False

    return True


async def handle_validation_commands(args):
    """Handle expert validation commands"""
    print_section_header("EXPERT VALIDATION")

    validator = DetectionValidator()

    if args.validate_action == "list":
        print("📋 Listing detections pending validation...")

        try:
            detections = await validator.get_pending_validations(
                priority_filter=getattr(args, 'priority', None),
                limit=getattr(args, 'limit', 20)
            )

            print(f"📊 Found {len(detections)} pending validations")
            for detection in detections:
                risk_level = detection.get('risk_level', 'Unknown')
                class_name = detection.get('class_name', 'Unknown')
                confidence = detection.get('confidence', 0.0)
                print(f"   • ID: {detection.get('id')} | {class_name} | Risk: {risk_level} | Confidence: {confidence:.2f}")

        except Exception as e:
            print(f"❌ Failed to list validations: {e}")
            return False

    elif args.validate_action in ["approve", "reject"]:
        detection_id = args.detection_id
        expert_id = getattr(args, 'expert_id', None)
        notes = getattr(args, 'notes', None)

        action = args.validate_action
        print(f"✅ {action.title()}ing detection {detection_id}...")

        try:
            success = await validator.validate_detection(
                detection_id=detection_id,
                action=action,
                expert_id=expert_id,
                validation_notes=notes
            )

            if success:
                print(f"✅ Detection {detection_id} {action}d successfully")
            else:
                print(f"❌ Failed to {action} detection {detection_id}")
                return False

        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False

    return True


async def create_sample_data(include_sample: bool = False):
    """Create sample data for testing"""
    print_section_header("SAMPLE DATA CREATION")

    if not include_sample:
        print("Creación de datos de muestra saltada (usar --sample-data para incluir)")
        return

    from src.database.models.models import UserProfile as User, Analysis, Detection
    from src.utils.database_utils import get_db_context

    with get_db_context() as db:
        # Create sample user if not exists
        existing_user = db.query(User).filter(User.email == "expert@sentrix.com").first()
        if not existing_user:
            sample_user = User(
                email="expert@sentrix.com",
                display_name="Expert User",
                organization="Sentrix Research",
                role=UserRoleEnum.EXPERT,
                is_active=True,
                is_verified=True
            )
            db.add(sample_user)
            db.commit()
            print("✅ Created sample expert user: expert@sentrix.com")
        else:
            print("ℹ️  Sample user already exists")

        print("✅ Sample data creation completed")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Sentrix Backend CLI - Sistema de Detección de Criaderos de Aedes aegypti"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Database commands
    db_parser = subparsers.add_parser('db', help='Database management')
    db_parser.add_argument('db_action', choices=['status', 'migrate', 'info'],
                          help='Database action to perform')

    # Analysis commands
    analyze_parser = subparsers.add_parser('analyze', help='Image analysis')
    analyze_parser.add_argument('--image', required=True, help='Path to image file')
    analyze_parser.add_argument('--user-id', type=int, help='User ID for analysis')
    analyze_parser.add_argument('--confidence', type=float, default=0.5,
                               help='Confidence threshold (0.1-1.0)')

    # Batch analysis
    batch_parser = subparsers.add_parser('batch', help='Batch image analysis')
    batch_parser.add_argument('--directory', required=True, help='Directory containing images')
    batch_parser.add_argument('--user-id', type=int, help='User ID for analysis')
    batch_parser.add_argument('--confidence', type=float, default=0.5,
                             help='Confidence threshold (0.1-1.0)')

    # Validation commands
    validate_parser = subparsers.add_parser('validate', help='Expert validation')
    validate_subparsers = validate_parser.add_subparsers(dest='validate_action')

    # List pending validations
    list_parser = validate_subparsers.add_parser('list', help='List pending validations')
    list_parser.add_argument('--priority', choices=['high_risk', 'medium_risk', 'low_risk'],
                           help='Filter by priority level')
    list_parser.add_argument('--limit', type=int, default=20, help='Maximum results')

    # Approve/reject validations
    for action in ['approve', 'reject']:
        action_parser = validate_subparsers.add_parser(action, help=f'{action.title()} detection')
        action_parser.add_argument('--detection-id', required=True,
                                 help='Detection ID to validate')
        action_parser.add_argument('--expert-id', type=int,
                                 help='Expert user ID performing validation')
        action_parser.add_argument('--notes', help='Validation notes')

    # Setup commands
    setup_parser = subparsers.add_parser('setup', help='Initial setup')
    setup_parser.add_argument('--sample-data', action='store_true',
                             help='Create sample data for testing')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run appropriate async handler
    async def run_command():
        try:
            if args.command == 'db':
                return await handle_database_commands(args)
            elif args.command == 'analyze':
                return await handle_analysis_commands(args)
            elif args.command == 'batch':
                return await handle_analysis_commands(args)
            elif args.command == 'validate':
                return await handle_validation_commands(args)
            elif args.command == 'setup':
                await create_sample_data(args.sample_data)
                return True
            else:
                print(f"❌ Unknown command: {args.command}")
                return False

        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    # Run the async command
    success = asyncio.run(run_command())

    if not success:
        print_section_header("OPERATION FAILED")
        sys.exit(1)
    else:
        print_section_header("OPERATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()