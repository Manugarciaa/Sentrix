#!/usr/bin/env python3
"""
Simple validation script without Unicode characters
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Test basic imports work"""
    print("Testing basic imports...")

    try:
        # Test shared library imports
        from shared.data_models import DetectionRiskEnum, BreedingSiteTypeEnum
        print("  [OK] Shared library imports work")

        # Test enum values
        assert DetectionRiskEnum.ALTO == "ALTO"
        assert BreedingSiteTypeEnum.BASURA == "Basura"
        print("  [OK] Enum values correct")

        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False

def test_port_configuration():
    """Test port configuration"""
    print("Testing port configuration...")

    try:
        from shared.config_manager import YoloServiceConfig
        config = YoloServiceConfig()

        if "8001" in config.url:
            print("  [OK] YOLO service configured for port 8001")
            return True
        else:
            print(f"  [FAIL] Wrong port in config: {config.url}")
            return False
    except Exception as e:
        print(f"  [FAIL] Configuration error: {e}")
        return False

def test_backend_schemas():
    """Test backend schema imports"""
    print("Testing backend schemas...")

    try:
        sys.path.insert(0, str(project_root / "backend"))
        from shared.data_models import ValidationStatusEnum

        # Test backward compatibility
        assert hasattr(ValidationStatusEnum, 'PENDING')
        print("  [OK] Backend schemas import correctly")
        return True
    except Exception as e:
        print(f"  [FAIL] Schema error: {e}")
        return False

def main():
    """Run validation tests"""
    print("Sentrix Simple Validation")
    print("=" * 40)

    tests = [
        test_basic_imports,
        test_port_configuration,
        test_backend_schemas,
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("SUCCESS: All validations passed!")
        return True
    else:
        print("FAILURE: Some validations failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)