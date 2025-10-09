#!/usr/bin/env python3
"""
Test script for image deduplication functionality
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Set testing mode to suppress warnings
os.environ['TESTING_MODE'] = 'true'

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend" / "src"))
sys.path.insert(0, str(project_root / "shared"))

def test_deduplication_functionality():
    """Test the image deduplication system"""
    print("=== Testing Image Deduplication System ===")

    try:
        from shared.image_deduplication import (
            calculate_content_signature,
            check_image_duplicate,
            get_deduplication_manager,
            estimate_storage_savings
        )

        print("[OK] Deduplication modules imported successfully")

        # Test content signature calculation
        test_image_data = b"fake_image_data_for_testing"
        signature = calculate_content_signature(test_image_data)

        required_keys = ['sha256', 'md5', 'size_bytes']
        for key in required_keys:
            if key not in signature:
                print(f"[ERROR] Missing signature key: {key}")
                return False

        print(f"[OK] Content signature: {signature['sha256'][:16]}... ({signature['size_bytes']} bytes)")

        # Test duplicate detection with no existing analyses
        duplicate_check = check_image_duplicate(test_image_data, [])
        if duplicate_check['is_duplicate'] or duplicate_check['should_store_separately'] != True:
            print(f"[ERROR] New image incorrectly detected as duplicate")
            return False

        print("[OK] New image correctly identified as unique")

        # Test duplicate detection with existing analysis
        existing_analyses = [
            {
                'id': 'test-analysis-1',
                'content_hash': signature['sha256'],
                'image_size_bytes': signature['size_bytes'],
                'image_url': 'https://example.com/test.jpg',
                'camera_make': 'Apple',
                'camera_model': 'iPhone 15',
                'has_gps_data': True,
                'gps_latitude': -34.603722,
                'gps_longitude': -58.381592
            }
        ]

        duplicate_check = check_image_duplicate(
            test_image_data,
            existing_analyses,
            camera_info={'camera_make': 'Apple', 'camera_model': 'iPhone 15'},
            gps_data={'has_gps': True, 'latitude': -34.603722, 'longitude': -58.381592}
        )

        if not duplicate_check['is_duplicate']:
            print(f"[ERROR] Duplicate image not detected")
            return False

        if duplicate_check['duplicate_type'] != 'exact_content':
            print(f"[ERROR] Wrong duplicate type: {duplicate_check['duplicate_type']}")
            return False

        if duplicate_check['should_store_separately'] != False:
            print(f"[ERROR] Duplicate should not be stored separately")
            return False

        print(f"[OK] Duplicate detected correctly with confidence: {duplicate_check['confidence']:.2f}")

        # Test storage savings calculation
        mock_analyses = [
            {'is_duplicate_reference': False, 'image_size_bytes': 1024000},
            {'is_duplicate_reference': True, 'storage_saved_bytes': 512000},
            {'is_duplicate_reference': True, 'storage_saved_bytes': 768000},
            {'is_duplicate_reference': False, 'image_size_bytes': 2048000}
        ]

        savings = estimate_storage_savings(mock_analyses)

        if savings['total_analyses'] != 4:
            print(f"[ERROR] Wrong total analyses count: {savings['total_analyses']}")
            return False

        if savings['duplicate_references'] != 2:
            print(f"[ERROR] Wrong duplicate count: {savings['duplicate_references']}")
            return False

        if savings['storage_saved_bytes'] != 1280000:
            print(f"[ERROR] Wrong storage savings: {savings['storage_saved_bytes']}")
            return False

        print(f"[OK] Storage savings calculation: {savings['storage_saved_mb']} MB saved ({savings['deduplication_rate']}% deduplication rate)")

        return True

    except Exception as e:
        print(f"[ERROR] Deduplication test failed: {e}")
        return False

def test_analysis_service_integration():
    """Test that analysis service properly integrates deduplication"""
    print("\n=== Testing Analysis Service Deduplication Integration ===")

    try:
        from services.analysis_service import AnalysisService

        service = AnalysisService()
        print("[OK] AnalysisService created successfully")

        # Check that deduplication methods exist
        required_methods = [
            '_get_recent_analyses_for_deduplication',
            '_handle_duplicate_image',
            'get_deduplication_stats'
        ]

        for method_name in required_methods:
            if not hasattr(service, method_name):
                print(f"[ERROR] Missing deduplication method: {method_name}")
                return False

        print("[OK] All deduplication methods available in AnalysisService")

        # Test deduplication stats method (should work even with no data)
        try:
            stats = service.get_deduplication_stats()
            if 'total_analyses' not in stats:
                print(f"[ERROR] Invalid deduplication stats format")
                return False
            print(f"[OK] Deduplication stats: {stats}")
        except Exception as e:
            print(f"[ERROR] get_deduplication_stats failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] Analysis service integration test failed: {e}")
        return False

def main():
    """Run deduplication tests"""
    print("Sentrix Deduplication System Test Suite")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    tests = [
        ("Deduplication Functionality", test_deduplication_functionality),
        ("Analysis Service Integration", test_analysis_service_integration)
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

    print("\n" + "=" * 50)
    print("DEDUPLICATION TEST RESULTS")
    print("=" * 50)
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n[SUCCESS] Deduplication system is working correctly!")
        print("Storage overflow problem has been solved.")
        print("Duplicate images will be detected and referenced instead of stored.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed.")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)