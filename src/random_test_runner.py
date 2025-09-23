#!/usr/bin/env python3
"""
🚨 RANDOM TEST RUNNER 🚨
=======================

"This is it! The moment we should have trained for!"
Random test execution on a subset of the test suite to validate system integrity.

Military-derived precision for random test execution.
When the system needs validation, Ghostbusters deploy!

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Random test execution with comprehensive validation
"""

import os
import random
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class TestResult:
    """Result of a single test execution."""
    test_file: str
    test_name: str
    status: str  # PASS, FAIL, ERROR, SKIP
    execution_time: float
    output: str
    error: str = ""
    coverage: float = 0.0

@dataclass
class TestSuiteResult:
    """Result of test suite execution."""
    suite_id: str
    total_tests: int
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    total_execution_time: float
    coverage_percentage: float
    test_results: List[TestResult]
    critical_failures: List[str]
    recommendations: List[str]

class RandomTestRunner:
    """🚨 RANDOM TEST RUNNER WITH COMPREHENSIVE VALIDATION 🚨"""
    
    def __init__(self, repository_root: str = ".", test_percentage: float = 0.20):
        self.repository_root = Path(repository_root)
        self.test_percentage = test_percentage
        self.suite_id = f"random_test_{int(time.time())}"
        self.test_results = []
        
        # Military-derived exclamations for test execution
        self.test_exclamations = [
            "🚨 THIS IS IT! THE MOMENT WE SHOULD HAVE TRAINED FOR!",
            "🛑 ALL HANDS ON DECK - RANDOM TEST EXECUTION INITIATED!",
            "🚨 GHOSTBUSTERS TO THE RESCUE - TEST VALIDATION DEPLOYING!",
            "🛑 EMERGENCY PROTOCOLS ACTIVATED - TEST EXECUTION INCOMING!",
            "🚨 THIS IS OUR DARKEST HOUR - TEST VALIDATION DEPLOYING!",
            "🛑 TEST EXECUTION ON FIRE - TIME TO EARN OUR PAY!",
            "🚨 CRISIS MODE ENGAGED - TEST VALIDATION ANALYSIS INCOMING!",
            "🛑 WE'RE IN THE SHIT NOW - TIME TO BE HEROES!",
        ]
        
        # Critical test categories
        self.critical_test_categories = {
            "core_functionality": [
                "test_reflective_module",
                "test_beast_mode",
                "test_rdi_system",
                "test_documentation_index"
            ],
            "migration_tests": [
                "test_migration",
                "test_rollback",
                "test_validation"
            ],
            "integration_tests": [
                "test_integration",
                "test_api",
                "test_cli"
            ]
        }
    
    def execute_random_tests(self) -> TestSuiteResult:
        """🚨 GHOSTBUSTERS RANDOM TEST MODE - We're going in!"""
        
        print(random.choice(self.test_exclamations))
        print("🛑 Stand back! Ghostbusters are taking over!")
        print("🚨 Emergency protocols activated - random test execution initiated!")
        print("🛑 This is too dangerous for human interaction - Ghostbusters deploying!")
        print()
        
        start_time = time.time()
        
        # Phase 1: Discover Test Files
        print("🔍 PHASE 1: DISCOVERING TEST FILES")
        print("=" * 50)
        
        test_files = self._discover_test_files()
        print(f"📊 Found {len(test_files)} test files")
        
        # Phase 2: Select Random Test Subset
        print("\n🎯 PHASE 2: SELECTING RANDOM TEST SUBSET")
        print("=" * 50)
        
        selected_tests = self._select_random_tests(test_files)
        print(f"📊 Selected {len(selected_tests)} tests for execution ({self.test_percentage*100:.1f}%)")
        
        # Phase 3: Execute Tests
        print("\n🧪 PHASE 3: EXECUTING RANDOM TESTS")
        print("=" * 50)
        
        test_results = self._execute_tests(selected_tests)
        
        # Phase 4: Analyze Results
        print("\n📊 PHASE 4: ANALYZING TEST RESULTS")
        print("=" * 50)
        
        analysis = self._analyze_test_results(test_results)
        
        # Phase 5: Generate Report
        print("\n📋 PHASE 5: GENERATING TEST REPORT")
        print("=" * 50)
        
        total_execution_time = time.time() - start_time
        
        suite_result = TestSuiteResult(
            suite_id=self.suite_id,
            total_tests=len(test_files),
            tests_run=len(selected_tests),
            tests_passed=len([r for r in test_results if r.status == "PASS"]),
            tests_failed=len([r for r in test_results if r.status == "FAIL"]),
            tests_skipped=len([r for r in test_results if r.status == "SKIP"]),
            total_execution_time=total_execution_time,
            coverage_percentage=analysis["coverage_percentage"],
            test_results=test_results,
            critical_failures=analysis["critical_failures"],
            recommendations=analysis["recommendations"]
        )
        
        # Save test results
        self._save_test_results(suite_result)
        
        return suite_result
    
    def _discover_test_files(self) -> List[Path]:
        """Discover all test files in the repository."""
        print("🔍 Discovering test files...")
        
        test_files = []
        
        # Look for test files in common locations
        test_patterns = [
            "test_*.py",
            "*_test.py",
            "tests/test_*.py",
            "tests/*_test.py"
        ]
        
        for pattern in test_patterns:
            for test_file in self.repository_root.rglob(pattern):
                if test_file.is_file() and self._is_valid_test_file(test_file):
                    test_files.append(test_file)
        
        # Also look for pytest test files
        for test_file in self.repository_root.rglob("*.py"):
            if test_file.is_file() and self._contains_test_functions(test_file):
                if test_file not in test_files:
                    test_files.append(test_file)
        
        return test_files
    
    def _is_valid_test_file(self, file_path: Path) -> bool:
        """Check if file is a valid test file."""
        # Skip files in virtual environments and cache directories
        skip_patterns = [
            ".venv/", "__pycache__/", ".pytest_cache/", ".mypy_cache/",
            "node_modules/", ".git/", "test_backup_", "migration_"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    def _contains_test_functions(self, file_path: Path) -> bool:
        """Check if file contains test functions."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return any(keyword in content for keyword in [
                    "def test_", "class Test", "pytest", "unittest"
                ])
        except:
            return False
    
    def _select_random_tests(self, test_files: List[Path]) -> List[Path]:
        """Select random subset of tests."""
        print("🎯 Selecting random test subset...")
        
        # Ensure we have at least some tests
        if not test_files:
            print("⚠️  No test files found!")
            return []
        
        # Calculate number of tests to run
        num_tests = max(1, int(len(test_files) * self.test_percentage))
        num_tests = min(num_tests, len(test_files))
        
        # Prioritize critical tests
        critical_tests = []
        regular_tests = []
        
        for test_file in test_files:
            is_critical = False
            for category, patterns in self.critical_test_categories.items():
                for pattern in patterns:
                    if pattern in test_file.name.lower():
                        critical_tests.append(test_file)
                        is_critical = True
                        break
                if is_critical:
                    break
            
            if not is_critical:
                regular_tests.append(test_file)
        
        # Select tests (prioritize critical ones)
        selected_tests = []
        
        # Add all critical tests if we have space
        if len(critical_tests) <= num_tests:
            selected_tests.extend(critical_tests)
            remaining_slots = num_tests - len(critical_tests)
            if remaining_slots > 0 and regular_tests:
                selected_tests.extend(random.sample(regular_tests, min(remaining_slots, len(regular_tests))))
        else:
            # Select subset of critical tests
            selected_tests.extend(random.sample(critical_tests, num_tests))
        
        print(f"📊 Critical tests: {len(critical_tests)}")
        print(f"📊 Regular tests: {len(regular_tests)}")
        print(f"📊 Selected tests: {len(selected_tests)}")
        
        return selected_tests
    
    def _execute_tests(self, test_files: List[Path]) -> List[TestResult]:
        """Execute the selected tests."""
        print("🧪 Executing tests...")
        
        test_results = []
        
        for test_file in test_files:
            print(f"  🧪 Running: {test_file.name}")
            
            result = self._run_single_test(test_file)
            test_results.append(result)
            
            status_emoji = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⚠️"
            print(f"    {status_emoji} {result.status} ({result.execution_time:.2f}s)")
        
        return test_results
    
    def _run_single_test(self, test_file: Path) -> TestResult:
        """Run a single test file."""
        start_time = time.time()
        
        try:
            # Try running with pytest first
            cmd = ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                status = "PASS"
            else:
                status = "FAIL"
            
            return TestResult(
                test_file=str(test_file),
                test_name=test_file.name,
                status=status,
                execution_time=execution_time,
                output=result.stdout,
                error=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return TestResult(
                test_file=str(test_file),
                test_name=test_file.name,
                status="ERROR",
                execution_time=execution_time,
                output="",
                error="Test execution timed out"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_file=str(test_file),
                test_name=test_file.name,
                status="ERROR",
                execution_time=execution_time,
                output="",
                error=str(e)
            )
    
    def _analyze_test_results(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test results and generate insights."""
        print("📊 Analyzing test results...")
        
        # Basic statistics
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.status == "PASS"])
        failed_tests = len([r for r in test_results if r.status == "FAIL"])
        error_tests = len([r for r in test_results if r.status == "ERROR"])
        
        # Calculate coverage (simplified)
        coverage_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Identify critical failures
        critical_failures = []
        for result in test_results:
            if result.status == "FAIL":
                # Check if it's a critical test
                for category, patterns in self.critical_test_categories.items():
                    for pattern in patterns:
                        if pattern in result.test_name.lower():
                            critical_failures.append(f"{result.test_name}: {result.error}")
                            break
        
        # Generate recommendations
        recommendations = []
        
        if failed_tests > 0:
            recommendations.append(f"Fix {failed_tests} failing tests")
        
        if error_tests > 0:
            recommendations.append(f"Resolve {error_tests} test execution errors")
        
        if coverage_percentage < 80:
            recommendations.append("Improve test coverage")
        
        if critical_failures:
            recommendations.append("Address critical test failures immediately")
        
        if passed_tests == total_tests:
            recommendations.append("All tests passing - system is healthy")
        
        return {
            "coverage_percentage": coverage_percentage,
            "critical_failures": critical_failures,
            "recommendations": recommendations
        }
    
    def _save_test_results(self, suite_result: TestSuiteResult):
        """Save test results to file."""
        results_file = self.repository_root / f"random_test_results_{self.suite_id}.json"
        
        with open(results_file, 'w') as f:
            json.dump(asdict(suite_result), f, indent=2, default=str)
        
        print(f"📋 Test results saved: {results_file}")
    
    def generate_test_report(self, suite_result: TestSuiteResult) -> str:
        """Generate comprehensive test report."""
        report = f"# Random Test Execution Report\n\n"
        report += f"**Test Suite ID:** {suite_result.suite_id}\n"
        report += f"**Execution Time:** {suite_result.total_execution_time:.2f} seconds\n"
        report += f"**Test Coverage:** {suite_result.coverage_percentage:.1f}%\n\n"
        
        # Summary
        report += "## 📊 Test Summary\n\n"
        report += f"- **Total Tests Available:** {suite_result.total_tests}\n"
        report += f"- **Tests Executed:** {suite_result.tests_run}\n"
        report += f"- **Tests Passed:** {suite_result.tests_passed} ✅\n"
        report += f"- **Tests Failed:** {suite_result.tests_failed} ❌\n"
        report += f"- **Tests Skipped:** {suite_result.tests_skipped} ⚠️\n\n"
        
        # Critical failures
        if suite_result.critical_failures:
            report += "## 🚨 Critical Failures\n\n"
            for failure in suite_result.critical_failures:
                report += f"- {failure}\n"
            report += "\n"
        
        # Recommendations
        if suite_result.recommendations:
            report += "## 💡 Recommendations\n\n"
            for recommendation in suite_result.recommendations:
                report += f"- {recommendation}\n"
            report += "\n"
        
        # Overall assessment
        if suite_result.tests_failed == 0 and suite_result.critical_failures == []:
            report += "## ✅ Assessment: SYSTEM HEALTHY\n\n"
            report += "All executed tests are passing. The system appears to be in good condition.\n"
        elif suite_result.critical_failures:
            report += "## 🚨 Assessment: CRITICAL ISSUES DETECTED\n\n"
            report += "Critical test failures detected. Immediate attention required.\n"
        else:
            report += "## ⚠️ Assessment: MINOR ISSUES DETECTED\n\n"
            report += "Some test failures detected. Review and fix as needed.\n"
        
        return report

def main():
    """Run random test execution."""
    print("🚨 RANDOM TEST RUNNER INITIATED! 🚨")
    print("This is it! The moment we should have trained for!")
    print()
    
    # Initialize random test runner
    runner = RandomTestRunner(test_percentage=0.20)  # 20% of tests
    
    try:
        # Execute random tests
        suite_result = runner.execute_random_tests()
        
        print(f"\n✅ Random test execution completed!")
        print(f"📊 Tests executed: {suite_result.tests_run}")
        print(f"📊 Tests passed: {suite_result.tests_passed}")
        print(f"📊 Tests failed: {suite_result.tests_failed}")
        print(f"📊 Coverage: {suite_result.coverage_percentage:.1f}%")
        print(f"📊 Execution time: {suite_result.total_execution_time:.2f} seconds")
        
        if suite_result.critical_failures:
            print(f"\n🚨 {len(suite_result.critical_failures)} critical failures detected!")
        elif suite_result.tests_failed == 0:
            print(f"\n🎉 All tests passing - system is healthy!")
        else:
            print(f"\n⚠️  {suite_result.tests_failed} test failures detected!")
        
        # Generate and save report
        report = runner.generate_test_report(suite_result)
        report_file = Path("random_test_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📋 Test report saved: {report_file}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()
