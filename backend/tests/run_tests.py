#!/usr/bin/env python3
"""
Test runner script for Sentrix Backend
Similar to the yolo-service test structure but adapted for backend
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_section_header(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def run_command(command, description, capture_output=False):
    """Run a shell command and handle errors"""
    print(f"\n=> {description}...")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout
        else:
            subprocess.run(command, shell=True, check=True)
        print(f"OK {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAIL {description} failed!")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error: {e.stderr}")
        return False


def run_unit_tests():
    """Run unit tests"""
    print_section_header("UNIT TESTS")
    return run_command(
        "pytest tests/test_models.py tests/test_yolo_integration.py -v -m 'not integration'",
        "Running unit tests"
    )


def run_integration_tests():
    """Run integration tests"""
    print_section_header("INTEGRATION TESTS")
    return run_command(
        "pytest tests/test_yolo_service_client.py -v -m 'not integration'",
        "Running integration tests"
    )


def run_api_tests():
    """Run API endpoint tests"""
    print_section_header("API TESTS")
    return run_command(
        "pytest tests/test_api_endpoints.py -v",
        "Running API endpoint tests"
    )


def run_system_tests():
    """Run complete system tests"""
    print_section_header("SYSTEM TESTS")

    # First run the standalone system test
    standalone_success = run_command(
        "python tests/test_complete_system.py",
        "Running standalone system tests"
    )

    # Then run pytest system tests
    pytest_success = run_command(
        "pytest tests/test_complete_system.py -v",
        "Running pytest system tests"
    )

    return standalone_success and pytest_success


def run_coverage_report():
    """Generate and display coverage report"""
    print_section_header("COVERAGE REPORT")

    # Run tests with coverage
    coverage_success = run_command(
        "pytest --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml",
        "Generating coverage report"
    )

    if coverage_success:
        print(f"\nCoverage report generated:")
        print(f"   - Terminal: shown above")
        print(f"   - HTML: htmlcov/index.html")
        print(f"   - XML: coverage.xml")

    return coverage_success


def run_linting():
    """Run code linting"""
    print_section_header("CODE LINTING")

    # Run Black formatter check
    black_success = run_command(
        "black --check --diff app tests",
        "Checking code formatting with Black"
    )

    # Run Ruff linter
    ruff_success = run_command(
        "ruff check app tests",
        "Running Ruff linter"
    )

    return black_success and ruff_success


def run_performance_tests():
    """Run performance tests"""
    print_section_header("PERFORMANCE TESTS")
    return run_command(
        "pytest tests/test_complete_system.py::TestSystemPerformance -v",
        "Running performance tests"
    )


def run_all_tests():
    """Run all tests in sequence"""
    print_section_header("RUNNING ALL TESTS")

    results = {
        "Unit Tests": run_unit_tests(),
        "Integration Tests": run_integration_tests(),
        "API Tests": run_api_tests(),
        "System Tests": run_system_tests(),
        "Code Linting": run_linting(),
        "Coverage Report": run_coverage_report(),
        "Performance Tests": run_performance_tests()
    }

    # Summary
    print_section_header("TEST RESULTS SUMMARY")
    passed = 0
    total = len(results)

    for test_name, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} test suites passed ({passed/total*100:.1f}%)")

    return passed == total


def check_dependencies():
    """Check if all required dependencies are installed"""
    print_section_header("CHECKING DEPENDENCIES")

    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "black",
        "ruff",
        "fastapi",
        "uvicorn"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"OK {package}")
        except ImportError:
            print(f"MISSING {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\nAll dependencies are installed")
    return True


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Sentrix Backend Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("--system", action="store_true", help="Run only system tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")

    args = parser.parse_args()

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"Working directory: {backend_dir}")

    success = True

    # Check dependencies first
    if args.check_deps or not any(vars(args).values()):
        if not check_dependencies():
            sys.exit(1)

    # Run specific tests based on arguments
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.api:
        success = run_api_tests()
    elif args.system:
        success = run_system_tests()
    elif args.coverage:
        success = run_coverage_report()
    elif args.lint:
        success = run_linting()
    elif args.performance:
        success = run_performance_tests()
    elif args.all or not any(vars(args).values()):
        success = run_all_tests()

    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()