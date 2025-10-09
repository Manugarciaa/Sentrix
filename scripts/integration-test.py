#!/usr/bin/env python3
"""
Sentrix Integration Test Script
Tests the complete system after implementing improvements from implement.md
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_port_configuration():
    """Test that port configuration is consistent"""
    print("[INFO] Testing port configuration consistency...")

    # Test environment variable loading
    from dotenv import load_dotenv
    load_dotenv()

    # Expected ports
    backend_port = int(os.getenv("BACKEND_PORT", "8000"))
    yolo_port = int(os.getenv("YOLO_SERVICE_PORT", "8001"))

    print(f"   Backend port: {backend_port}")
    print(f"   YOLO service port: {yolo_port}")

    # Verify port configuration in config files
    from backend.config.settings import get_settings
    backend_settings = get_settings()

    # Check if YOLO service URL uses correct port
    expected_yolo_url = f"http://localhost:{yolo_port}"
    if expected_yolo_url in backend_settings.external_services.yolo_service_url:
        print("   ✅ Backend → YOLO service URL configuration correct")
    else:
        print(f"   ❌ Backend → YOLO service URL mismatch: {backend_settings.external_services.yolo_service_url}")
        return False

    return True


def test_shared_library_imports():
    """Test that shared library imports work consistently"""
    print("[INFO] Testing shared library imports...")

    try:
        # Test backend imports from shared
        sys.path.insert(0, str(project_root / "backend"))
        from shared.data_models import (
            DetectionRiskEnum, BreedingSiteTypeEnum, AnalysisStatusEnum,
            ValidationStatusEnum, UserRoleEnum, RiskLevelEnum, LocationSourceEnum
        )
        print("   ✅ Backend can import shared enums")

        # Test YOLO service imports from shared
        sys.path.insert(0, str(project_root / "yolo-service"))
        from shared.data_models import DetectionRiskEnum as YoloDetectionRiskEnum
        print("   ✅ YOLO service can import shared enums")

        # Test enum values consistency
        assert DetectionRiskEnum.ALTO == "ALTO"
        assert BreedingSiteTypeEnum.BASURA == "Basura"
        assert UserRoleEnum.ADMIN == "ADMIN"
        print("   ✅ Enum values are consistent")

        # Test that ValidationStatusEnum has PENDING for backward compatibility
        assert hasattr(ValidationStatusEnum, 'PENDING')
        assert ValidationStatusEnum.PENDING == "pending"
        print("   ✅ Backward compatibility maintained")

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"   ❌ Enum value mismatch: {e}")
        return False


def test_risk_assessment_consistency():
    """Test that risk assessment works consistently"""
    print("[INFO] Testing risk assessment consistency...")

    try:
        from shared.risk_assessment import assess_dengue_risk
        from shared.data_models import DetectionRiskEnum, BreedingSiteTypeEnum

        # Test sample detections
        sample_detections = [
            {
                "class": "Charcos/Cumulo de agua",
                "confidence": 0.85,
                "risk_level": "ALTO"
            },
            {
                "class": "Basura",
                "confidence": 0.75,
                "risk_level": "MEDIO"
            }
        ]

        risk_result = assess_dengue_risk(sample_detections)

        # Check that result has expected structure
        expected_keys = ["total_detections", "risk_distribution", "overall_risk_level"]
        for key in expected_keys:
            if key not in risk_result:
                print(f"   ❌ Missing key in risk assessment: {key}")
                return False

        print("   ✓ Risk assessment function working")
        print(f"   [REPORT] Sample result: {risk_result['overall_risk_level']}")

        return True

    except Exception as e:
        print(f"   ❌ Risk assessment error: {e}")
        return False


def test_configuration_system():
    """Test centralized configuration system"""
    print("[INFO] Testing centralized configuration system...")

    try:
        # Test .env file loading
        env_example = project_root / ".env.example"
        if not env_example.exists():
            print("   ❌ .env.example file not found")
            return False

        print("   ✅ .env.example file exists")

        # Test that required environment variables are defined
        with open(env_example, 'r') as f:
            env_content = f.read()

        required_vars = [
            "BACKEND_PORT", "YOLO_SERVICE_PORT", "DATABASE_URL",
            "SECRET_KEY", "JWT_SECRET_KEY", "YOLO_MODEL_PATH"
        ]

        for var in required_vars:
            if var not in env_content:
                print(f"   ❌ Missing required variable in .env.example: {var}")
                return False

        print("   ✅ All required environment variables defined")

        # Test shared config manager
        from shared.config_manager import YoloServiceConfig
        yolo_config = YoloServiceConfig()

        # Check that default URL uses correct port
        if "8001" in yolo_config.url:
            print("   ✅ Shared config manager uses correct port")
        else:
            print(f"   ❌ Shared config manager port mismatch: {yolo_config.url}")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Configuration test error: {e}")
        return False


def test_documentation_consistency():
    """Test that documentation is updated correctly"""
    print("[INFO] Testing documentation consistency...")

    try:
        # Check import conventions documentation
        import_doc = project_root / "shared" / "IMPORT_CONVENTIONS.md"
        if not import_doc.exists():
            print("   ❌ Import conventions documentation not found")
            return False

        print("   ✅ Import conventions documentation exists")

        # Check that documentation mentions correct ports
        with open(import_doc, 'r') as f:
            doc_content = f.read()

        if "Port 8001" in doc_content and "YOLO Service" in doc_content:
            print("   ✅ Documentation mentions correct YOLO service port")
        else:
            print("   ⚠️  Documentation may not reflect correct ports")

        # Check for shared import examples
        if "from shared.data_models import" in doc_content:
            print("   ✅ Documentation shows correct import pattern")
        else:
            print("   ❌ Documentation missing shared import examples")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Documentation test error: {e}")
        return False


def test_backend_integration():
    """Test backend integration with shared library"""
    print("[INFO] Testing backend integration...")

    try:
        sys.path.insert(0, str(project_root / "backend"))

        # Test that schemas import from shared correctly
        from backend.src.schemas.analyses import AnalysisUploadRequest
        print("   ✅ Backend schemas import successfully")

        # Test that app can start (just import, don't run)
        from backend.app.main import app
        if app.title:
            print(f"   ✅ Backend app initializes: {app.title}")

        return True

    except Exception as e:
        print(f"   ❌ Backend integration error: {e}")
        return False


def test_yolo_service_integration():
    """Test YOLO service integration with shared library"""
    print("[INFO] Testing YOLO service integration...")

    try:
        sys.path.insert(0, str(project_root / "yolo-service"))

        # Test that YOLO service can import shared components
        from shared.data_models import DetectionRiskEnum
        print("   ✅ YOLO service can import shared enums")

        # Test that YOLO service server can initialize
        # (Just test imports, not actual server start)
        import yolo_service.server as yolo_server
        if hasattr(yolo_server, 'app'):
            print("   ✅ YOLO service app can be imported")

        return True

    except Exception as e:
        print(f"   ❌ YOLO service integration error: {e}")
        return False


def main():
    """Run all integration tests"""
    print("[START] Sentrix Integration Test Suite")
    print("Testing improvements from implement.md")
    print("=" * 50)

    tests = [
        ("Port Configuration", test_port_configuration),
        ("Shared Library Imports", test_shared_library_imports),
        ("Risk Assessment Consistency", test_risk_assessment_consistency),
        ("Configuration System", test_configuration_system),
        ("Documentation Consistency", test_documentation_consistency),
        ("Backend Integration", test_backend_integration),
        ("YOLO Service Integration", test_yolo_service_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n[INFO] {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"   ✓ PASSED")
            else:
                print(f"   X FAILED")
        except Exception as e:
            print(f"   X ERROR: {e}")

    print("\n" + "=" * 50)
    print(f"[REPORT] INTEGRATION TEST RESULTS")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        print("✓ implement.md improvements successfully validated")
        return True
    else:
        print("[WARN] Some integration tests failed")
        print("[TIP] Check the output above for details")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)