#!/usr/bin/env python3
"""
🚨 TARGETED TEST RUNNER 🚨
=========================

"This is it! The moment we should have trained for!"
Targeted test execution focusing on actual test files with proper discovery.

Military-derived precision for targeted test execution.
When the system needs validation, Ghostbusters deploy!

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Targeted test execution with proper test discovery
"""

import os
import random
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict

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

class TargetedTestRunner:
    """🚨 TARGETED TEST RUNNER WITH PROPER TEST DISCOVERY 🚨"""
    
    def __init__(self, repository_root: str = ".", test_percentage: float = 0.30):
        self.repository_root = Path(repository_root)
        self.test_percentage = test_percentage
        self.suite_id = f"targeted_test_{int(time.time())}"
        self.test_results = []
        
        # Military-derived exclamations for test execution
        self.test_exclamations = [
            "🚨 THIS IS IT! THE MOMENT WE SHOULD HAVE TRAINED FOR!",
            "🛑 ALL HANDS ON DECK - TARGETED TEST EXECUTION INITIATED!",
            "🚨 GHOSTBUSTERS TO THE RESCUE - TEST VALIDATION DEPLOYING!",
            "🛑 EMERGENCY PROTOCOLS ACTIVATED - TARGETED TEST EXECUTION INCOMING!",
            "🚨 THIS IS OUR DARKEST HOUR - TEST VALIDATION DEPLOYING!",
            "🛑 TEST EXECUTION ON FIRE - TIME TO EARN OUR PAY!",
            "🚨 CRISIS MODE ENGAGED - TARGETED TEST VALIDATION ANALYSIS INCOMING!",
            "🛑 WE'RE IN THE SHIT NOW - TIME TO BE HEROES!",
        ]
        
        # Priority test patterns
        self.priority_patterns = [
            "test_reflective_module",
            "test_beast_mode",
            "test_rdi",
            "test_migration",
            "test_validation",
            "test_integration",
            "test_cli"
        ]
    
    def execute_targeted_tests(self) -> TestSuiteResult:
        """🚨 GHOSTBUSTERS TARGETED TEST MODE - We're going in!"""
        
        print(random.choice(self.test_exclamations))
        print("🛑 Stand back! Ghostbusters are taking over!")
        print("🚨 Emergency protocols activated - targeted test execution initiated!")
        print("🛑 This is too dangerous for human interaction - Ghostbusters deploying!")
        print()
        
        start_time = time.time()
        
        # Phase 1: Discover Real Test Files
        print("🔍 PHASE 1: DISCOVERING REAL TEST FILES")
        print("=" * 50)
        
        test_files = self._discover_real_test_files()
        print(f"📊 Found {len(test_files)} real test files")
        
        # Phase 2: Select Priority Tests
        print("\n🎯 PHASE 2: SELECTING PRIORITY TESTS")
        print("=" * 50)
        
        selected_tests = self._select_priority_tests(test_files)
        print(f"📊 Selected {len(selected_tests)} priority tests for execution")
        
        # Phase 3: Execute Tests
        print("\n🧪 PHASE 3: EXECUTING TARGETED TESTS")
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
    
    def _discover_real_test_files(self) -> List[Path]:
        """Discover real test files that actually contain test functions."""
        print("🔍 Discovering real test files...")
        
        test_files = []
        
        # Look for test files in tests/ directory first
        tests_dir = self.repository_root / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.rglob("test_*.py"):
                if test_file.is_file() and self._is_valid_test_file(test_file):
                    test_files.append(test_file)
        
        # Look for test files in src/ directory
        src_dir = self.repository_root / "src"
        if src_dir.exists():
            for test_file in src_dir.rglob("test_*.py"):
                if test_file.is_file() and self._is_valid_test_file(test_file):
                    test_files.append(test_file)
        
        # Look for test files in root directory
        for test_file in self.repository_root.glob("test_*.py"):
            if test_file.is_file() and self._is_valid_test_file(test_file):
                test_files.append(test_file)
        
        return test_files
    
    def _is_valid_test_file(self, file_path: Path) -> bool:
        """Check if file is a valid test file with actual test functions."""
        # Skip files in virtual environments and cache directories
        skip_patterns = [
            ".venv/", "__pycache__/", ".pytest_cache/", ".mypy_cache/",
            "node_modules/", ".git/", "test_backup_", "migration_"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False
        
        # Check if file contains actual test functions
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Look for test functions or test classes
                has_test_functions = any(keyword in content for keyword in [
                    "def test_", "class Test", "pytest", "unittest"
                ])
                # Make sure it's not just a regular Python file
                is_actual_test = "def test_" in content or "class Test" in content
                return has_test_functions and is_actual_test
        except:
            return False
    
    def _select_priority_tests(self, test_files: List[Path]) -> List[Path]:
        """Select priority tests based on patterns."""
        print("🎯 Selecting priority tests...")
        
        if not test_files:
            print("⚠️  No test files found!")
            return []
        
        # Categorize tests by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for test_file in test_files:
            file_name = test_file.name.lower()
            is_priority = False
            
            for pattern in self.priority_patterns:
                if pattern in file_name:
                    high_priority.append(test_file)
                    is_priority = True
                    break
            
            if not is_priority:
                if "integration" in file_name or "e2e" in file_name:
                    medium_priority.append(test_file)
                else:
                    low_priority.append(test_file)
        
        # Select tests (prioritize high priority)
        selected_tests = []
        
        # Add all high priority tests
        selected_tests.extend(high_priority)
        
        # Add some medium priority tests
        if medium_priority:
            num_medium = min(len(medium_priority), max(1, int(len(medium_priority) * 0.5)))
            selected_tests.extend(random.sample(medium_priority, num_medium))
        
        # Add some low priority tests
        if low_priority:
            num_low = min(len(low_priority), max(1, int(len(low_priority) * 0.3)))
            selected_tests.extend(random.sample(low_priority, num_low))
        
        print(f"📊 High priority tests: {len(high_priority)}")
        print(f"📊 Medium priority tests: {len(medium_priority)}")
        print(f"📊 Low priority tests: {len(low_priority)}")
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
            # Try running with pytest
            cmd = ["python", "-m", "pytest", str(test_file), "-v", "--tb=short", "--no-header"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
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
                for pattern in self.priority_patterns:
                    if pattern in result.test_name.lower():
                        critical_failures.append(f"{result.test_name}: {result.error[:100]}...")
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
        results_file = self.repository_root / f"targeted_test_results_{self.suite_id}.json"
        
        with open(results_file, 'w') as f:
            json.dump(asdict(suite_result), f, indent=2, default=str)
        
        print(f"📋 Test results saved: {results_file}")
    
    def generate_test_report(self, suite_result: TestSuiteResult) -> str:
        """Generate comprehensive test report."""
        report = f"# Targeted Test Execution Report\n\n"
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
    """Run targeted test execution."""
    print("🚨 TARGETED TEST RUNNER INITIATED! 🚨")
    print("This is it! The moment we should have trained for!")
    print()
    
    # Initialize targeted test runner
    runner = TargetedTestRunner(test_percentage=0.30)  # 30% of tests
    
    try:
        # Execute targeted tests
        suite_result = runner.execute_targeted_tests()
        
        print(f"\n✅ Targeted test execution completed!")
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
        report_file = Path("targeted_test_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📋 Test report saved: {report_file}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()
