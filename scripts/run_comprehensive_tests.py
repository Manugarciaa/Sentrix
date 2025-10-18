#!/usr/bin/env python3
"""
Comprehensive test runner for Sentrix image processing system
Script de pruebas exhaustivas para el sistema de procesamiento de imágenes Sentrix

This script runs all tests and generates a comprehensive report.
Este script ejecuta todas las pruebas y genera un reporte exhaustivo.
"""

import os
import sys
import subprocess
import time
import json
import psutil
from datetime import datetime
from pathlib import Path
import unittest
import coverage
from io import StringIO

# Add project root to sys.path for imports (if needed when running standalone)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))


class TestResult:
    """Container for test results"""
    def __init__(self):
        self.suite_name = ""
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.execution_time = 0.0
        self.details = []
        self.coverage_percentage = 0.0


class ComprehensiveTestRunner:
    """Main test runner for comprehensive testing"""

    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        self.system_info = self._get_system_info()
        self.test_suites = [
            {
                "name": "Standardized Naming System",
                "path": "shared/tests/test_standardized_naming.py",
                "description": "Tests for filename generation and parsing"
            },
            {
                "name": "Dual Image Storage",
                "path": "backend/tests/test_dual_image_storage.py",
                "description": "Tests for image storage and Supabase integration"
            },
            {
                "name": "YOLO-Backend Integration",
                "path": "backend/tests/test_yolo_backend_integration.py",
                "description": "Tests for YOLO service integration"
            },
            {
                "name": "Performance and Load Testing",
                "path": "backend/tests/test_performance_load.py",
                "description": "Performance benchmarks and load testing"
            },
            {
                "name": "Edge Cases and Error Handling",
                "path": "backend/tests/test_edge_cases_errors.py",
                "description": "Edge cases and error condition handling"
            }
        ]

    def _get_system_info(self):
        """Get system information for the test report"""
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "timestamp": datetime.now().isoformat()
        }

    def run_all_tests(self, with_coverage=True):
        """Run all test suites"""
        print("[START] Starting Comprehensive Test Suite for Sentrix Image Processing System")
        print("=" * 80)
        print(f"[TIME] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[SYSTEM] System: {self.system_info['platform']} | CPU: {self.system_info['cpu_count']} cores | RAM: {self.system_info['memory_total_gb']} GB")
        print("=" * 80)

        self.start_time = time.time()

        # Initialize coverage if requested
        cov = None
        if with_coverage:
            try:
                cov = coverage.Coverage()
                cov.start()
                print("[REPORT] Coverage tracking enabled")
            except ImportError:
                print("[WARN] Coverage package not available, running without coverage")
                with_coverage = False

        # Run each test suite
        for suite_config in self.test_suites:
            print(f"\n[INFO] Running: {suite_config['name']}")
            print(f"[NOTE] {suite_config['description']}")
            print("-" * 60)

            result = self._run_test_suite(suite_config)
            self.results.append(result)

            # Print immediate results
            self._print_suite_result(result)

        self.end_time = time.time()

        # Stop coverage and get report
        if with_coverage and cov:
            cov.stop()
            cov.save()

            # Generate coverage report
            for result in self.results:
                try:
                    coverage_percent = cov.report(show_missing=False)
                    result.coverage_percentage = coverage_percent
                except:
                    result.coverage_percentage = 0.0

        # Generate final report
        self._generate_final_report()

    def _run_test_suite(self, suite_config):
        """Run a single test suite"""
        result = TestResult()
        result.suite_name = suite_config['name']

        test_path = project_root / suite_config['path']

        if not test_path.exists():
            result.error_tests = 1
            result.details.append(f"Test file not found: {test_path}")
            return result

        start_time = time.time()

        try:
            # Capture test output
            test_output = StringIO()

            # Load and run the test module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(str(test_path).replace('/', '.').replace('\\', '.').replace('.py', ''))

            runner = unittest.TextTestRunner(stream=test_output, verbosity=2)
            test_result = runner.run(suite)

            # Extract results
            result.total_tests = test_result.testsRun
            result.passed_tests = test_result.testsRun - len(test_result.failures) - len(test_result.errors) - len(test_result.skipped)
            result.failed_tests = len(test_result.failures)
            result.error_tests = len(test_result.errors)
            result.skipped_tests = len(test_result.skipped)

            # Capture details
            for failure in test_result.failures:
                result.details.append(f"FAILURE: {failure[0]} - {failure[1]}")

            for error in test_result.errors:
                result.details.append(f"ERROR: {error[0]} - {error[1]}")

        except Exception as e:
            result.error_tests = 1
            result.details.append(f"Test suite execution error: {str(e)}")

        result.execution_time = time.time() - start_time
        return result

    def _print_suite_result(self, result):
        """Print results for a single test suite"""
        total_time = result.execution_time

        if result.error_tests > 0 and result.total_tests == 0:
            print(f"X SUITE ERROR - {result.suite_name}")
        elif result.failed_tests == 0 and result.error_tests == 0:
            print(f"✓ PASSED - {result.suite_name}")
        else:
            print(f"[WARN] ISSUES - {result.suite_name}")

        print(f"   [REPORT] Tests: {result.total_tests} | ✓ {result.passed_tests} | X {result.failed_tests} | X {result.error_tests} | [INFO] {result.skipped_tests}")
        print(f"   [TIME] Time: {total_time:.2f}s")

        if result.coverage_percentage > 0:
            print(f"   [METRICS] Coverage: {result.coverage_percentage:.1f}%")

        if result.details:
            print(f"   [WARN] Issues found: {len(result.details)}")

    def _generate_final_report(self):
        """Generate comprehensive final report"""
        total_time = self.end_time - self.start_time

        # Calculate totals
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed_tests for r in self.results)
        total_failed = sum(r.failed_tests for r in self.results)
        total_errors = sum(r.error_tests for r in self.results)
        total_skipped = sum(r.skipped_tests for r in self.results)

        # Overall status
        overall_success = (total_failed == 0 and total_errors == 0)

        print("\n" + "=" * 80)
        print("[REPORT] COMPREHENSIVE TEST REPORT")
        print("=" * 80)

        # Overall summary
        if overall_success:
            print("[SUCCESS] OVERALL STATUS: ALL TESTS PASSED")
        else:
            print("[WARN] OVERALL STATUS: ISSUES FOUND")

        print(f"[TIME] Total Execution Time: {total_time:.2f} seconds")
        print(f"[INFO] Total Test Suites: {len(self.results)}")
        print(f"[INFO] Total Tests: {total_tests}")
        print(f"✓ Passed: {total_passed}")
        print(f"X Failed: {total_failed}")
        print(f"X Errors: {total_errors}")
        print(f"[INFO] Skipped: {total_skipped}")

        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"[METRICS] Success Rate: {success_rate:.1f}%")

        # Detailed results by suite
        print("\n[INFO] DETAILED RESULTS BY SUITE:")
        print("-" * 60)

        for result in self.results:
            suite_success = (result.failed_tests == 0 and result.error_tests == 0)
            status_icon = "✓" if suite_success else "X"

            print(f"\n{status_icon} {result.suite_name}")
            print(f"   [REPORT] {result.total_tests} tests | ✓ {result.passed_tests} | X {result.failed_tests} | X {result.error_tests}")
            print(f"   [TIME] {result.execution_time:.2f}s")

            if result.coverage_percentage > 0:
                print(f"   [METRICS] Coverage: {result.coverage_percentage:.1f}%")

            # Show first few issues if any
            if result.details:
                print(f"   [WARN] Issues ({len(result.details)}):")
                for i, detail in enumerate(result.details[:3]):  # Show first 3
                    print(f"      [INFO] {detail[:100]}...")
                if len(result.details) > 3:
                    print(f"      ... and {len(result.details) - 3} more")

        # Performance summary
        self._generate_performance_summary()

        # Recommendations
        self._generate_recommendations()

        # Save report to file
        self._save_report_to_file()

        print("\n" + "=" * 80)
        print("[COMPLETE] TEST EXECUTION COMPLETED")
        print("=" * 80)

    def _generate_performance_summary(self):
        """Generate performance analysis"""
        print("\n[PERFORMANCE] PERFORMANCE ANALYSIS:")
        print("-" * 40)

        suite_times = [(r.suite_name, r.execution_time) for r in self.results]
        suite_times.sort(key=lambda x: x[1], reverse=True)

        print("[TIME] Execution times by suite:")
        for name, time_taken in suite_times:
            print(f"   {name}: {time_taken:.2f}s")

        # Memory usage
        memory_usage = psutil.virtual_memory()
        print(f"\n[SAVE] Memory usage: {memory_usage.percent:.1f}% ({memory_usage.used / (1024**3):.1f}GB used)")

    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        print("\n[TIP] RECOMMENDATIONS:")
        print("-" * 30)

        has_failures = any(r.failed_tests > 0 or r.error_tests > 0 for r in self.results)

        if not has_failures:
            print("✓ All tests passing! System is ready for production.")
            print("   [INFO] Consider running performance tests under load")
            print("   [INFO] Monitor system in production environment")
        else:
            print("[WARN] Issues found that need attention:")

            for result in self.results:
                if result.failed_tests > 0 or result.error_tests > 0:
                    print(f"   [INFO] Fix issues in {result.suite_name}")

            print("\n[MAINTAIN] Next steps:")
            print("   1. Review failed test details above")
            print("   2. Fix identified issues")
            print("   3. Re-run tests until all pass")
            print("   4. Consider adding more edge case tests")

        # Coverage recommendations
        low_coverage_suites = [r for r in self.results if 0 < r.coverage_percentage < 80]
        if low_coverage_suites:
            print(f"\n[METRICS] Consider improving test coverage for:")
            for result in low_coverage_suites:
                print(f"   [INFO] {result.suite_name}: {result.coverage_percentage:.1f}%")

    def _save_report_to_file(self):
        """Save detailed report to JSON file"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.system_info,
            "total_execution_time": self.end_time - self.start_time,
            "summary": {
                "total_tests": sum(r.total_tests for r in self.results),
                "total_passed": sum(r.passed_tests for r in self.results),
                "total_failed": sum(r.failed_tests for r in self.results),
                "total_errors": sum(r.error_tests for r in self.results),
                "total_skipped": sum(r.skipped_tests for r in self.results)
            },
            "suites": []
        }

        for result in self.results:
            suite_data = {
                "name": result.suite_name,
                "total_tests": result.total_tests,
                "passed_tests": result.passed_tests,
                "failed_tests": result.failed_tests,
                "error_tests": result.error_tests,
                "skipped_tests": result.skipped_tests,
                "execution_time": result.execution_time,
                "coverage_percentage": result.coverage_percentage,
                "details": result.details
            }
            report_data["suites"].append(suite_data)

        # Save to file
        report_file = project_root / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n[SAVE] Detailed report saved to: {report_file}")


def main():
    """Main entry point"""
    print("[INFO] Sentrix Image Processing System - Comprehensive Test Suite")
    print("=" * 80)

    # Check if all required packages are available
    missing_packages = []
    try:
        import psutil
    except ImportError:
        missing_packages.append("psutil")

    try:
        import coverage
    except ImportError:
        print("[INFO] Coverage package not available (optional)")

    if missing_packages:
        print(f"X Missing required packages: {', '.join(missing_packages)}")
        print("   Install with: pip install " + " ".join(missing_packages))
        return 1

    # Run tests
    runner = ComprehensiveTestRunner()

    try:
        runner.run_all_tests(with_coverage=True)
        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\nX Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)