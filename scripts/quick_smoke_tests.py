#!/usr/bin/env python3
"""
Quick smoke tests for Sentrix image processing system
Pruebas rápidas de funcionamiento básico del sistema

These are fast tests to verify basic functionality is working.
Estas son pruebas rápidas para verificar que la funcionalidad básica funciona.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Set testing mode to suppress warnings
os.environ['TESTING_MODE'] = 'true'

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend" / "src"))
sys.path.insert(0, str(project_root / "shared"))


def test_imports():
    """Test that all critical modules can be imported"""
    print("Testing imports...")

    tests = [
        ("Shared file utils", "shared.file_utils"),
        ("Shared image formats", "shared.image_formats"),
        ("Backend analysis service", "services.analysis_service"),
        ("Backend Supabase client", "utils.supabase_client"),
        ("Backend YOLO client", "core.services.yolo_service"),
    ]

    failures = []

    for test_name, module_name in tests:
        try:
            __import__(module_name)
            print(f"  [OK] {test_name}")
        except ImportError as e:
            print(f"  [ERROR] {test_name}: {e}")
            failures.append((test_name, str(e)))

    return len(failures) == 0, failures


def test_filename_generation():
    """Test basic filename generation"""
    print("\nTesting filename generation...")

    try:
        from shared.file_utils import generate_standardized_filename, parse_standardized_filename

        # Test basic generation
        filename = generate_standardized_filename(
            original_filename="IMG_1234.jpg",
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )

        if not filename.startswith("SENTRIX_20250926_143052"):
            return False, f"Generated filename has wrong format: {filename}"

        # Test parsing
        parsed = parse_standardized_filename(filename)
        if not parsed['is_standardized']:
            return False, f"Failed to parse generated filename: {filename}"

        print(f"  [OK] Generated and parsed: {filename}")

        # Test with GPS data
        gps_filename = generate_standardized_filename(
            original_filename="IMG_1234.jpg",
            gps_data={"has_gps": True, "latitude": -34.603722, "longitude": -58.381592},
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )

        if "LAT" not in gps_filename or "LON" not in gps_filename:
            return False, f"GPS data not properly encoded in filename: {gps_filename}"

        print(f"  [OK] GPS encoding: {gps_filename}")

        return True, None

    except Exception as e:
        return False, str(e)


def test_image_format_detection():
    """Test image format detection and conversion"""
    print("\nTesting image format detection...")

    try:
        from shared.image_formats import detect_image_format, is_format_supported

        # Test format detection
        test_cases = [
            ("test.jpg", True),
            ("test.png", True),
            ("test.heic", True),
            ("test.unknown", False)
        ]

        for filename, should_be_supported in test_cases:
            supported = is_format_supported(filename)
            if supported != should_be_supported:
                return False, f"Format support check failed for {filename}"

            format_info = detect_image_format(BytesIO(b"fake_data") if filename != "test.unknown" else filename)
            if should_be_supported and not format_info.get('supported', False):
                return False, f"Format detection failed for {filename}"

        print("  [OK] Format detection working")
        return True, None

    except Exception as e:
        return False, str(e)


def test_supabase_client_creation():
    """Test Supabase client can be created (without actual connection)"""
    print("\nTesting Supabase client creation...")

    try:
        from utils.supabase_client import SupabaseManager

        # This should not fail even without valid credentials
        manager = SupabaseManager()

        # Test that methods exist
        required_methods = ['upload_image', 'upload_dual_images', 'delete_image', 'insert_analysis']
        for method_name in required_methods:
            if not hasattr(manager, method_name):
                return False, f"Missing method: {method_name}"

        print("  [OK] Supabase client structure valid")
        return True, None

    except Exception as e:
        return False, str(e)


def test_yolo_client_creation():
    """Test YOLO client can be created"""
    print("\nTesting YOLO client creation...")

    try:
        from core.services.yolo_service import YOLOServiceClient

        client = YOLOServiceClient()

        # Test that methods exist
        required_methods = ['detect_image', 'health_check', 'get_available_models']
        for method_name in required_methods:
            if not hasattr(client, method_name):
                return False, f"Missing method: {method_name}"

        print("  [OK] YOLO client structure valid")
        return True, None

    except Exception as e:
        return False, str(e)


def test_analysis_service_creation():
    """Test analysis service can be created"""
    print("\nTesting analysis service creation...")

    try:
        from services.analysis_service import AnalysisService

        service = AnalysisService()

        # Test that methods exist
        required_methods = ['process_image_analysis', 'get_analysis_by_id', 'list_analyses']
        for method_name in required_methods:
            if not hasattr(service, method_name):
                return False, f"Missing method: {method_name}"

        # Test that required attributes exist
        if not hasattr(service, 'supabase'):
            return False, "Missing supabase attribute"

        if not hasattr(service, 'yolo_client'):
            return False, "Missing yolo_client attribute"

        print("  [OK] Analysis service structure valid")
        return True, None

    except Exception as e:
        return False, str(e)


def test_filename_variations():
    """Test filename variations generation"""
    print("\nTesting filename variations...")

    try:
        from shared.file_utils import create_filename_variations

        variations = create_filename_variations(
            base_filename="IMG_1234.jpg",
            camera_info={"camera_make": "Apple", "camera_model": "iPhone 15"}
        )

        required_keys = ['original', 'standardized', 'processed', 'thumbnail', 'analysis_id', 'timestamp']
        for key in required_keys:
            if key not in variations:
                return False, f"Missing variation key: {key}"

        # Check that processed filename has correct prefix
        if not variations['processed'].startswith("SENTRIX_PROC_"):
            return False, f"Processed filename has wrong format: {variations['processed']}"

        # Check that thumbnail has correct suffix
        if not variations['thumbnail'].endswith("_thumb.jpg"):
            return False, f"Thumbnail filename has wrong format: {variations['thumbnail']}"

        print("  [OK] Filename variations working")
        return True, None

    except Exception as e:
        return False, str(e)


def main():
    """Run all smoke tests"""
    print("Sentrix Image Processing - Quick Smoke Tests")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    start_time = time.time()

    tests = [
        ("Imports", test_imports),
        ("Filename Generation", test_filename_generation),
        ("Image Format Detection", test_image_format_detection),
        ("Supabase Client", test_supabase_client_creation),
        ("YOLO Client", test_yolo_client_creation),
        ("Analysis Service", test_analysis_service_creation),
        ("Filename Variations", test_filename_variations),
    ]

    passed = 0
    failed = 0
    failures = []

    for test_name, test_func in tests:
        try:
            success, error = test_func()
            if success:
                passed += 1
            else:
                failed += 1
                failures.append((test_name, error))
        except Exception as e:
            failed += 1
            failures.append((test_name, f"Unexpected error: {str(e)}"))

    end_time = time.time()
    total_time = end_time - start_time

    # Results
    print("\n" + "=" * 60)
    print("SMOKE TEST RESULTS")
    print("=" * 60)

    if failed == 0:
        print("ALL SMOKE TESTS PASSED!")
        print("   Basic functionality is working correctly.")
    else:
        print("SOME SMOKE TESTS FAILED")
        print("   Basic functionality issues detected.")

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_time:.2f} seconds")

    if failures:
        print("\nFAILURES:")
        for test_name, error in failures:
            print(f"   - {test_name}: {error}")

    print("\n" + "=" * 60)
    if failed == 0:
        print("SYSTEM READY - You can run the comprehensive tests")
        print("   Next: python scripts/run_comprehensive_tests.py")
    else:
        print("FIX ISSUES BEFORE RUNNING FULL TESTS")
        print("   Fix the failures above and run smoke tests again")

    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    from io import BytesIO  # Import here to avoid issues with main imports

    exit_code = main()
    sys.exit(exit_code)