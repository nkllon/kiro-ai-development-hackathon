#!/usr/bin/env python3
"""
Integration Test Runner - Comprehensive validation system
=======================================================

This script runs comprehensive integration tests to validate the entire
system including syntax validation, RDI compliance, and prevention measures.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Integration testing for prevention framework
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of an integration test."""

    test_name: str
    passed: bool
    message: str
    duration: float
    details: Dict[str, Any] = None


class IntegrationTestRunner:
    """Runs comprehensive integration tests."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results = []
        self.start_time = datetime.now()

    def run_syntax_validation_test(self) -> TestResult:
        """Test syntax validation system."""
        start_time = datetime.now()

        try:
            # Test Python syntax validation
            result = subprocess.run(
                ["python3", "scripts/code_generation_validator.py", "src"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            passed = result.returncode == 0

            return TestResult(
                test_name="Syntax Validation",
                passed=passed,
                message=(
                    "Syntax validation completed successfully"
                    if passed
                    else "Syntax validation failed"
                ),
                duration=(datetime.now() - start_time).total_seconds(),
                details={
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Syntax Validation",
                passed=False,
                message=f"Syntax validation test failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": str(e)},
            )

    def run_indentation_validation_test(self) -> TestResult:
        """Test indentation validation system."""
        start_time = datetime.now()

        try:
            # Test indentation validation
            result = subprocess.run(
                [
                    "python3",
                    "scripts/indentation_validator.py",
                    "src/beast_mode/tool_health/tool_health_manager_services_part_26.py",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            passed = result.returncode == 0

            return TestResult(
                test_name="Indentation Validation",
                passed=passed,
                message=(
                    "Indentation validation completed successfully"
                    if passed
                    else "Indentation validation failed"
                ),
                duration=(datetime.now() - start_time).total_seconds(),
                details={
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Indentation Validation",
                passed=False,
                message=f"Indentation validation test failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": str(e)},
            )

    def run_rdi_test_validation(self) -> TestResult:
        """Test RDI test execution."""
        start_time = datetime.now()

        try:
            # Test RDI test execution
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "pytest",
                    "tests/unit/beast_mode/tool_health/test_tool_health_manager_services_part_26_rdi_traceable.py",
                    "-v",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            passed = result.returncode == 0

            return TestResult(
                test_name="RDI Test Validation",
                passed=passed,
                message=(
                    "RDI tests executed successfully" if passed else "RDI tests failed"
                ),
                duration=(datetime.now() - start_time).total_seconds(),
                details={
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="RDI Test Validation",
                passed=False,
                message=f"RDI test validation failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": str(e)},
            )

    def run_template_generation_test(self) -> TestResult:
        """Test code generation templates."""
        start_time = datetime.now()

        try:
            # Test template generation
            result = subprocess.run(
                ["python3", "scripts/code_generation_templates.py", "--list"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            passed = result.returncode == 0

            return TestResult(
                test_name="Template Generation",
                passed=passed,
                message=(
                    "Template generation system working"
                    if passed
                    else "Template generation failed"
                ),
                duration=(datetime.now() - start_time).total_seconds(),
                details={
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Template Generation",
                passed=False,
                message=f"Template generation test failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": str(e)},
            )

    def run_prevention_framework_test(self) -> TestResult:
        """Test prevention framework components."""
        start_time = datetime.now()

        try:
            # Check if all prevention components exist
            components = [
                "scripts/code_generation_validator.py",
                "scripts/indentation_validator.py",
                "scripts/code_generation_templates.py",
                ".pre-commit-config.yaml",
                ".github/workflows/syntax-validation.yml",
            ]

            missing_components = []
            for component in components:
                if not Path(component).exists():
                    missing_components.append(component)

            passed = len(missing_components) == 0

            return TestResult(
                test_name="Prevention Framework",
                passed=passed,
                message=(
                    "All prevention components present"
                    if passed
                    else f"Missing components: {missing_components}"
                ),
                duration=(datetime.now() - start_time).total_seconds(),
                details={
                    "missing_components": missing_components,
                    "total_components": len(components),
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Prevention Framework",
                passed=False,
                message=f"Prevention framework test failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": str(e)},
            )

    def run_all_tests(self) -> List[TestResult]:
        """Run all integration tests."""
        print("🚀 RUNNING COMPREHENSIVE INTEGRATION TESTS")
        print("=" * 60)

        tests = [
            self.run_syntax_validation_test,
            self.run_indentation_validation_test,
            self.run_rdi_test_validation,
            self.run_template_generation_test,
            self.run_prevention_framework_test,
        ]

        for test_func in tests:
            print(f"\n🔍 Running {test_func.__name__}...")
            result = test_func()
            self.test_results.append(result)

            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"{status}: {result.message} ({result.duration:.2f}s)")

            if not result.passed and result.details:
                if "error" in result.details:
                    print(f"   Error: {result.details['error']}")
                if "stderr" in result.details and result.details["stderr"]:
                    print(f"   Details: {result.details['stderr'][:200]}...")

        return self.test_results

    def generate_report(self) -> str:
        """Generate integration test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        total_duration = (datetime.now() - self.start_time).total_seconds()

        report = f"""
🔍 INTEGRATION TEST REPORT
=========================

📊 SUMMARY:
• Total Tests: {total_tests}
• Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
• Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
• Total Duration: {total_duration:.2f} seconds

📋 DETAILED RESULTS:
"""

        for result in self.test_results:
            status = "✅" if result.passed else "❌"
            report += f"{status} {result.test_name}: {result.message} ({result.duration:.2f}s)\n"

        if failed_tests > 0:
            report += f"""
⚠️  FAILURES DETECTED:
"""
            for result in self.test_results:
                if not result.passed:
                    report += f"• {result.test_name}: {result.message}\n"

        return report


def main():
    """Main integration test function."""
    runner = IntegrationTestRunner()

    # Run all tests
    results = runner.run_all_tests()

    # Generate and display report
    report = runner.generate_report()
    print(report)

    # Save report
    with open("integration_test_report.txt", "w") as f:
        f.write(report)

    print("📄 Report saved to integration_test_report.txt")

    # Exit with error code if any tests failed
    if any(not result.passed for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
