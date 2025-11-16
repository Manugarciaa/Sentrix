#!/usr/bin/env python3
"""
Simple test script for Sentrix image processing system functionality
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Set testing mode to suppress warnings
os.environ['TESTING_MODE'] = 'true'

# Add project root to sys.path for imports (if needed when running standalone)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))


def test_shared_functionality():
    """Test shared library functionality"""
    print("=== Testing Shared Library ===")

    try:
        from sentrix_shared import file_utils
        print("[OK] file_utils import successful")

        # Test filename generation
        filename = file_utils.generate_standardized_filename(
            'IMG_1234.jpg',
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )
        print(f"[OK] Generated filename: {filename}")

        # Test parsing
        parsed = file_utils.parse_standardized_filename(filename)
        if parsed['is_standardized']:
            print("[OK] Filename parsing successful")
        else:
            print("[ERROR] Filename parsing failed")
            return False

        # Test with GPS data
        gps_filename = file_utils.generate_standardized_filename(
            'IMG_1234.jpg',
            gps_data={'has_gps': True, 'latitude': -34.603722, 'longitude': -58.381592},
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )

        if 'LAT' in gps_filename and 'LON' in gps_filename:
            print(f"[OK] GPS encoding: {gps_filename}")
        else:
            print(f"[ERROR] GPS encoding failed: {gps_filename}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] Shared library test failed: {e}")
        return False


def test_backend_functionality():
    """Test backend functionality"""
    print("\n=== Testing Backend Services ===")

    try:
        from backend.src.services.analysis_service import AnalysisService
        print("[OK] AnalysisService import successful")

        service = AnalysisService()
        print("[OK] AnalysisService instantiation successful")

        # Check required methods
        required_methods = ['process_image_analysis', 'get_analysis_by_id', 'list_analyses']
        for method in required_methods:
            if hasattr(service, method):
                print(f"[OK] Method {method} available")
            else:
                print(f"[ERROR] Method {method} NOT available")
                return False

        return True

    except Exception as e:
        print(f"[ERROR] Backend test failed: {e}")
        return False


def test_supabase_client():
    """Test Supabase client functionality"""
    print("\n=== Testing Supabase Client ===")

    try:
        from backend.src.utils.supabase_client import SupabaseManager
        print("[OK] SupabaseManager import successful")

        manager = SupabaseManager()
        print("[OK] SupabaseManager instantiation successful")

        # Check new methods
        new_methods = ['upload_image', 'upload_dual_images', 'delete_image']
        for method in new_methods:
            if hasattr(manager, method):
                print(f"[OK] New method {method} available")
            else:
                print(f"[ERROR] New method {method} NOT available")
                return False

        # Test content type detection
        if hasattr(manager, '_get_content_type'):
            jpg_type = manager._get_content_type('.jpg')
            png_type = manager._get_content_type('.png')

            if jpg_type == 'image/jpeg' and png_type == 'image/png':
                print("[OK] Content type detection working")
            else:
                print(f"[ERROR] Content type detection failed: jpg={jpg_type}, png={png_type}")
                return False

        return True

    except Exception as e:
        print(f"[ERROR] Supabase client test failed: {e}")
        return False


def test_complete_workflow():
    """Test complete workflow simulation"""
    print("\n=== Testing Complete Workflow ===")

    try:
        from backend.src.services.analysis_service import generate_standardized_filename, create_filename_variations

        # Simulate complete workflow
        original_filename = "IMG_1234.jpg"
        camera_info = {"camera_make": "Apple", "camera_model": "iPhone 15"}
        gps_data = {"has_gps": True, "latitude": -34.603722, "longitude": -58.381592}

        # Generate standardized filename
        standardized = generate_standardized_filename(
            original_filename=original_filename,
            camera_info=camera_info,
            gps_data=gps_data,
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )
        print(f"[OK] Standardized filename: {standardized}")

        # Generate variations
        variations = create_filename_variations(
            base_filename=original_filename,
            camera_info=camera_info,
            gps_data=gps_data
        )

        required_variations = ['original', 'standardized', 'processed', 'thumbnail']
        for var in required_variations:
            if var in variations:
                print(f"[OK] Variation {var}: {variations[var]}")
            else:
                print(f"[ERROR] Missing variation: {var}")
                return False

        return True

    except Exception as e:
        print(f"[ERROR] Complete workflow test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Sentrix Image Processing System - Simple Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    start_time = time.time()

    tests = [
        ("Shared Library", test_shared_functionality),
        ("Backend Services", test_backend_functionality),
        ("Supabase Client", test_supabase_client),
        ("Complete Workflow", test_complete_workflow)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_func():
                print(f"[PASS] {test_name}")
                passed += 1
            else:
                print(f"[FAIL] {test_name}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name}: {e}")
            failed += 1

    end_time = time.time()
    total_time = end_time - start_time

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "0%")
    print(f"Execution time: {total_time:.2f} seconds")

    if failed == 0:
        print("\n[SUCCESS] All tests passed! System is functional.")
        print("Next step: You can run comprehensive tests or proceed with manual testing.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Review the issues above.")
        print("Fix the problems before proceeding to full testing.")

    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)