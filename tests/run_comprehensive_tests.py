#!/usr/bin/env python3
"""
Comprehensive Test Runner

This script provides a comprehensive test runner for the entire Beast Mode framework,
including unit tests, integration tests, performance tests, and coverage reporting.
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.test_utilities import TestConfig, TestEnvironment, PerformanceMonitor
from src.rm_ddd.core.base_reflective_module import ReflectiveModule, ModuleCapability, ModuleStatus, ModuleHealth



class TestRunner(ReflectiveModule):
    """Comprehensive test runner."""
    
    def __init__(self, config: TestConfig = None):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        self.config = config or TestConfig()
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.temp_dir = None
        self.coverage_data = {}
    
    def setup(self):
        """Set up test environment."""
        self.start_time = time.time()
        self.temp_dir = tempfile.mkdtemp(prefix="beast_mode_tests_")
        
        # Set up environment variables
        os.environ["BEAST_MODE_TEST_MODE"] = "true"
        os.environ["BEAST_MODE_LOG_LEVEL"] = self.config.log_level
        
        print(f"Test environment set up in: {self.temp_dir}")
        print(f"Test configuration: {self.config.__dict__}")
    
    def teardown(self):
        """Tear down test environment."""
        self.end_time = time.time()
        
        if self.config.cleanup_after and self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"Test environment cleaned up: {self.temp_dir}")
        
        # Print summary
        total_time = self.end_time - self.start_time
        print(f"\nTest execution completed in {total_time:.2f} seconds")
        self.print_summary()
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests."""
        print("\n" + "="*60)
        print("RUNNING UNIT TESTS")
        print("="*60)
        
        start_time = time.time()
        
        # Run unit tests
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            f"--timeout={self.config.timeout}",
            "--maxfail=10"
        ]
        
        if self.config.parallel_execution:
            cmd.extend(["-n", "auto"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        unit_results = {
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        self.results["unit_tests"] = unit_results
        
        print(f"Unit tests completed in {duration:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode != 0:
            print("Unit test failures:")
            print(result.stdout)
            print(result.stderr)
        
        return unit_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        start_time = time.time()
        
        # Run integration tests
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            f"--timeout={self.config.timeout * 2}",  # Longer timeout for integration
            "--maxfail=5"
        ]
        
        if self.config.parallel_execution:
            cmd.extend(["-n", "2"])  # Fewer parallel processes for integration
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        integration_results = {
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        self.results["integration_tests"] = integration_results
        
        print(f"Integration tests completed in {duration:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode != 0:
            print("Integration test failures:")
            print(result.stdout)
            print(result.stderr)
        
        return integration_results
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        print("\n" + "="*60)
        print("RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        start_time = time.time()
        
        # Run performance tests
        cmd = [
            "python", "-m", "pytest",
            "tests/performance/",
            "-v",
            "--tb=short",
            f"--timeout={self.config.timeout * 3}",  # Longer timeout for performance
            "--maxfail=3"
        ]
        
        # Performance tests should run sequentially
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        performance_results = {
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        self.results["performance_tests"] = performance_results
        
        print(f"Performance tests completed in {duration:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode != 0:
            print("Performance test failures:")
            print(result.stdout)
            print(result.stderr)
        
        return performance_results
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run coverage analysis."""
        print("\n" + "="*60)
        print("RUNNING COVERAGE ANALYSIS")
        print("="*60)
        
        start_time = time.time()
        
        # Run coverage analysis
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=json",
            "--cov-report=term",
            f"--cov-fail-under={self.config.coverage_threshold}",
            "-q"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        # Parse coverage data
        coverage_file = Path("coverage.json")
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
                self.coverage_data = coverage_data
        
        coverage_results = {
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "coverage_data": self.coverage_data
        }
        
        self.results["coverage_analysis"] = coverage_results
        
        print(f"Coverage analysis completed in {duration:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode != 0:
            print("Coverage analysis issues:")
            print(result.stdout)
            print(result.stderr)
        
        return coverage_results
    
    def run_linting(self) -> Dict[str, Any]:
        """Run code linting."""
        print("\n" + "="*60)
        print("RUNNING CODE LINTING")
        print("="*60)
        
        start_time = time.time()
        
        # Run flake8
        flake8_cmd = ["python", "-m", "flake8", "src/", "tests/"]
        flake8_result = subprocess.run(flake8_cmd, capture_output=True, text=True)
        
        # Run mypy
        mypy_cmd = ["python", "-m", "mypy", "src/"]
        mypy_result = subprocess.run(mypy_cmd, capture_output=True, text=True)
        
        # Run black check
        black_cmd = ["python", "-m", "black", "--check", "src/", "tests/"]
        black_result = subprocess.run(black_cmd, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        linting_results = {
            "duration": duration,
            "flake8": {
                "exit_code": flake8_result.returncode,
                "stdout": flake8_result.stdout,
                "stderr": flake8_result.stderr
            },
            "mypy": {
                "exit_code": mypy_result.returncode,
                "stdout": mypy_result.stdout,
                "stderr": mypy_result.stderr
            },
            "black": {
                "exit_code": black_result.returncode,
                "stdout": black_result.stdout,
                "stderr": black_result.stderr
            },
            "success": all(r.returncode == 0 for r in [flake8_result, mypy_result, black_result])
        }
        
        self.results["linting"] = linting_results
        
        print(f"Linting completed in {duration:.2f} seconds")
        print(f"Flake8: {flake8_result.returncode}")
        print(f"MyPy: {mypy_result.returncode}")
        print(f"Black: {black_result.returncode}")
        
        return linting_results
    
    def run_security_scan(self) -> Dict[str, Any]:
        """Run security scanning."""
        print("\n" + "="*60)
        print("RUNNING SECURITY SCAN")
        print("="*60)
        
        start_time = time.time()
        
        # Run bandit security scanner
        bandit_cmd = ["python", "-m", "bandit", "-r", "src/", "-f", "json"]
        bandit_result = subprocess.run(bandit_cmd, capture_output=True, text=True)
        
        # Run safety check for known vulnerabilities
        safety_cmd = ["python", "-m", "safety", "check", "--json"]
        safety_result = subprocess.run(safety_cmd, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        security_results = {
            "duration": duration,
            "bandit": {
                "exit_code": bandit_result.returncode,
                "stdout": bandit_result.stdout,
                "stderr": bandit_result.stderr
            },
            "safety": {
                "exit_code": safety_result.returncode,
                "stdout": safety_result.stdout,
                "stderr": safety_result.stderr
            },
            "success": bandit_result.returncode == 0 and safety_result.returncode == 0
        }
        
        self.results["security_scan"] = security_results
        
        print(f"Security scan completed in {duration:.2f} seconds")
        print(f"Bandit: {bandit_result.returncode}")
        print(f"Safety: {safety_result.returncode}")
        
        return security_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests."""
        print("Starting comprehensive test suite...")
        print(f"Configuration: {self.config.__dict__}")
        
        self.setup()
        
        try:
            # Run all test categories
            self.run_unit_tests()
            self.run_integration_tests()
            self.run_performance_tests()
            self.run_coverage_analysis()
            self.run_linting()
            self.run_security_scan()
            
            # Calculate overall success
            overall_success = all(
                result.get("success", False) 
                for result in self.results.values()
            )
            
            self.results["overall_success"] = overall_success
            
            return self.results
            
        finally:
            self.teardown()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_duration = self.end_time - self.start_time
        
        print(f"Total execution time: {total_duration:.2f} seconds")
        print(f"Overall success: {self.results.get('overall_success', False)}")
        
        print("\nTest Categories:")
        for category, result in self.results.items():
            if category == "overall_success":
                continue
            
            success = result.get("success", False)
            duration = result.get("duration", 0)
            status = "✓ PASS" if success else "✗ FAIL"
            
            print(f"  {category:20} {status:8} ({duration:.2f}s)")
        
        # Coverage summary
        if self.coverage_data:
            total_coverage = self.coverage_data.get("totals", {}).get("percent_covered", 0)
            print(f"\nCoverage: {total_coverage:.1f}%")
            
            if total_coverage < self.config.coverage_threshold:
                print(f"⚠️  Coverage below threshold: {total_coverage:.1f}% < {self.config.coverage_threshold}%")
        
        # Performance summary
        if "performance_tests" in self.results:
            perf_result = self.results["performance_tests"]
            if perf_result["success"]:
                print("\nPerformance: ✓ All performance tests passed")
            else:
                print("\nPerformance: ✗ Some performance tests failed")
        
        # Security summary
        if "security_scan" in self.results:
            sec_result = self.results["security_scan"]
            if sec_result["success"]:
                print("Security: ✓ No security issues found")
            else:
                print("Security: ✗ Security issues detected")
    
    def save_results(self, output_file: str = "test_results.json"):
        """Save test results to file."""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config.__dict__,
            "results": self.results,
            "coverage_data": self.coverage_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"Test results saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner")
    parser.add_argument("--timeout", type=int, default=30, help="Test timeout in seconds")
    parser.add_argument("--coverage-threshold", type=float, default=90.0, help="Coverage threshold")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel execution")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't cleanup temp files")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    parser.add_argument("--output", default="test_results.json", help="Output file for results")
    parser.add_argument("--category", choices=["unit", "integration", "performance", "coverage", "linting", "security", "all"], 
                       default="all", help="Test category to run")
    
    args = parser.parse_args()
    
    # Create test configuration
    config = TestConfig(
        timeout=args.timeout,
        coverage_threshold=args.coverage_threshold,
        parallel_execution=args.parallel,
        cleanup_after=not args.no_cleanup,
        log_level=args.log_level
    )
    
    # Create test runner
    runner = TestRunner(config)
    
    # Run tests based on category
    if args.category == "all":
        results = runner.run_all_tests()
    elif args.category == "unit":
        runner.setup()
        try:
            results = runner.run_unit_tests()
        finally:
            runner.teardown()
    elif args.category == "integration":
        runner.setup()
        try:
            results = runner.run_integration_tests()
        finally:
            runner.teardown()
    elif args.category == "performance":
        runner.setup()
        try:
            results = runner.run_performance_tests()
        finally:
            runner.teardown()
    elif args.category == "coverage":
        runner.setup()
        try:
            results = runner.run_coverage_analysis()
        finally:
            runner.teardown()
    elif args.category == "linting":
        runner.setup()
        try:
            results = runner.run_linting()
        finally:
            runner.teardown()
    elif args.category == "security":
        runner.setup()
        try:
            results = runner.run_security_scan()
        finally:
            runner.teardown()
    
    # Save results
    runner.save_results(args.output)
    
    # Exit with appropriate code
    overall_success = runner.results.get("overall_success", False)
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

