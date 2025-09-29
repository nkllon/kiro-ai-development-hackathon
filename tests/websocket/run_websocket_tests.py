#!/usr/bin/env python3
"""WebSocket Connectivity Test Suite Runner.

This script runs the comprehensive WebSocket test suite including:
- Unit tests for WebSocket manager, connection handler, and retry logic
- Integration tests for tunnel WebSocket connectivity
- Load tests for concurrent connections and message throughput
- Coverage validation to ensure >90% test coverage
"""

import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import pytest


class WebSocketTestRunner:
    """WebSocket test suite runner with coverage validation."""
    
    def __init__(self):
        self.test_results = {}
        self.coverage_results = {}
        self.start_time = None
        
    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests."""
        self.log_action("run_unit_tests", "in_progress")
        
        start_time = time.time()
        
        # Run unit tests with coverage
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/websocket/unit/",
            "-v",
            "--tb=short",
            "--cov=src/beast_mode/observatory/websocket",
            "--cov-report=json:coverage_unit.json",
            "--cov-report=term-missing"
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        unit_results = {
            "return_code": result.returncode,
            "duration_seconds": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        self.test_results["unit_tests"] = unit_results
        
        status = "completed" if result.returncode == 0 else "error"
        self.log_action("run_unit_tests", status, {
            "duration": duration,
            "passed": result.returncode == 0,
            "return_code": result.returncode
        })
        
        return unit_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        self.log_action("run_integration_tests", "in_progress")
        
        start_time = time.time()
        
        # Run integration tests with coverage
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/websocket/integration/",
            "-v",
            "--tb=short",
            "--cov=src/beast_mode/observatory/websocket",
            "--cov-report=json:coverage_integration.json",
            "--cov-report=term-missing"
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        integration_results = {
            "return_code": result.returncode,
            "duration_seconds": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        self.test_results["integration_tests"] = integration_results
        
        status = "completed" if result.returncode == 0 else "error"
        self.log_action("run_integration_tests", status, {
            "duration": duration,
            "passed": result.returncode == 0,
            "return_code": result.returncode
        })
        
        return integration_results
    
    def run_load_tests(self) -> Dict[str, Any]:
        """Run load tests."""
        self.log_action("run_load_tests", "in_progress")
        
        start_time = time.time()
        
        # Run load tests (may take longer)
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/websocket/load/",
            "-v",
            "--tb=short",
            "--timeout=1800",  # 30 minute timeout for load tests
            "-m", "not slow"  # Skip very slow tests by default
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        load_results = {
            "return_code": result.returncode,
            "duration_seconds": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        self.test_results["load_tests"] = load_results
        
        status = "completed" if result.returncode == 0 else "error"
        self.log_action("run_load_tests", status, {
            "duration": duration,
            "passed": result.returncode == 0,
            "return_code": result.returncode
        })
        
        return load_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests with comprehensive coverage."""
        self.log_action("run_all_tests", "in_progress")
        
        start_time = time.time()
        
        # Run all tests with coverage
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/websocket/",
            "-v",
            "--tb=short",
            "--cov=src/beast_mode/observatory/websocket",
            "--cov-report=json:coverage_all.json",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-fail-under=90"  # Require 90% coverage
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        all_results = {
            "return_code": result.returncode,
            "duration_seconds": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        self.test_results["all_tests"] = all_results
        
        status = "completed" if result.returncode == 0 else "error"
        self.log_action("run_all_tests", status, {
            "duration": duration,
            "passed": result.returncode == 0,
            "return_code": result.returncode
        })
        
        return all_results
    
    def validate_coverage(self) -> Dict[str, Any]:
        """Validate test coverage meets requirements."""
        self.log_action("validate_coverage", "in_progress")
        
        coverage_files = [
            "coverage_unit.json",
            "coverage_integration.json", 
            "coverage_all.json"
        ]
        
        coverage_results = {}
        
        for coverage_file in coverage_files:
            if Path(coverage_file).exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                    
                    coverage_results[coverage_file] = {
                        "total_coverage": total_coverage,
                        "meets_requirement": total_coverage >= 90.0,
                        "files_covered": len(coverage_data.get('files', {})),
                        "lines_covered": coverage_data.get('totals', {}).get('covered_lines', 0),
                        "lines_total": coverage_data.get('totals', {}).get('num_statements', 0)
                    }
                    
                except Exception as e:
                    coverage_results[coverage_file] = {
                        "error": str(e),
                        "meets_requirement": False
                    }
        
        self.coverage_results = coverage_results
        
        # Check if all coverage meets requirement
        all_meet_requirement = all(
            result.get("meets_requirement", False) 
            for result in coverage_results.values()
        )
        
        status = "completed" if all_meet_requirement else "error"
        self.log_action("validate_coverage", status, {
            "all_meet_requirement": all_meet_requirement,
            "coverage_results": coverage_results
        })
        
        return coverage_results
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        self.log_action("generate_test_report", "in_progress")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("passed", False))
        
        total_duration = sum(result.get("duration_seconds", 0) for result in self.test_results.values())
        
        report = {
            "test_suite": "WebSocket Connectivity Test Suite",
            "task": "6.1",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_test_suites": total_tests,
                "passed_test_suites": passed_tests,
                "failed_test_suites": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_duration_seconds": total_duration
            },
            "test_results": self.test_results,
            "coverage_results": self.coverage_results,
            "requirements_met": {
                "unit_tests": "✓" if self.test_results.get("unit_tests", {}).get("passed", False) else "✗",
                "integration_tests": "✓" if self.test_results.get("integration_tests", {}).get("passed", False) else "✗",
                "load_tests": "✓" if self.test_results.get("load_tests", {}).get("passed", False) else "✗",
                "coverage_90_percent": "✓" if all(
                    result.get("meets_requirement", False) 
                    for result in self.coverage_results.values()
                ) else "✗"
            }
        }
        
        # Save report
        with open("websocket_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        self.log_action("generate_test_report", "completed", {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": report["summary"]["success_rate"],
            "report_file": "websocket_test_report.json"
        })
        
        return report
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete WebSocket test suite."""
        self.log_action("run_full_test_suite", "in_progress")
        
        self.start_time = time.time()
        
        try:
            # Run all test suites
            self.run_unit_tests()
            self.run_integration_tests()
            self.run_load_tests()
            
            # Validate coverage
            self.validate_coverage()
            
            # Generate final report
            report = self.generate_test_report()
            
            total_duration = time.time() - self.start_time
            
            # Final status
            all_passed = all(
                result.get("passed", False) 
                for result in self.test_results.values()
            )
            
            status = "completed" if all_passed else "error"
            self.log_action("run_full_test_suite", status, {
                "total_duration": total_duration,
                "all_tests_passed": all_passed,
                "report_generated": True
            })
            
            return report
            
        except Exception as e:
            self.log_action("run_full_test_suite", "error", {"error": str(e)})
            raise


def main():
    """Main entry point for test runner."""
    runner = WebSocketTestRunner()
    
    try:
        report = runner.run_full_test_suite()
        
        print("\n" + "="*80)
        print("WEBSOCKET CONNECTIVITY TEST SUITE RESULTS")
        print("="*80)
        
        print(f"Task: {report['task']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total Duration: {report['summary']['total_duration_seconds']:.2f} seconds")
        print(f"Success Rate: {report['summary']['success_rate']:.2%}")
        
        print("\nRequirements Coverage:")
        for req, status in report['requirements_met'].items():
            print(f"  {req}: {status}")
        
        print("\nTest Suite Results:")
        for suite, result in report['test_results'].items():
            status = "PASSED" if result['passed'] else "FAILED"
            duration = result['duration_seconds']
            print(f"  {suite}: {status} ({duration:.2f}s)")
        
        print("\nCoverage Results:")
        for file, result in report['coverage_results'].items():
            if 'error' not in result:
                coverage = result['total_coverage']
                meets_req = "✓" if result['meets_requirement'] else "✗"
                print(f"  {file}: {coverage:.1f}% {meets_req}")
        
        print(f"\nDetailed report saved to: websocket_test_report.json")
        print("="*80)
        
        # Exit with appropriate code
        all_passed = report['summary']['success_rate'] == 1.0
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()