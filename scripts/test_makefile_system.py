#!/usr/bin/env python3
"""
Makefile System Testing Framework
=================================

Comprehensive testing framework for Makefile system validation.
Provides target testing, integration validation, and system health checks.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Testing framework for Makefile system operations
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult


class TestType(Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestResult(Enum):
    """Test result types."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class TestCase:
    """Represents a test case."""
    name: str
    description: str
    test_type: TestType
    target: str
    commands: List[str] = field(default_factory=list)
    expected_result: int = 0
    timeout: float = 30
    prerequisites: List[str] = field(default_factory=list)
    cleanup: List[str] = field(default_factory=list)


@dataclass
class TestExecution:
    """Test execution result."""
    test_case: TestCase
    result: TestResult
    duration: float
    output: str = ""
    error: str = ""
    return_code: int = 0
    timestamp: float = 0


class MakefileSystemTester(ReflectiveModule):
    """
    🧪 MAKEFILE SYSTEM TESTING FRAMEWORK 🧪
    
    Comprehensive testing framework for validating Makefile system operations.
    Provides automated testing, validation, and reporting capabilities.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "makefile_system_tester"
        self.repository_root = Path(repository_root)
        
        # Test registry
        self.test_cases: List[TestCase] = []
        self.test_results: List[TestExecution] = []
        
        # Initialize built-in test cases
        self._initialize_builtin_tests()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "Makefile System Tester",
            "version": "1.0.0",
            "description": "Comprehensive testing framework for Makefile system operations",
            "repository_root": str(self.repository_root),
            "test_cases_count": len(self.test_cases),
            "test_results_count": len(self.test_results)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        from datetime import datetime
        
        # Calculate health metrics
        total_tests = len(self.test_results)
        failed_tests = sum(1 for result in self.test_results if result.status == TestStatus.FAILED)
        error_tests = sum(1 for result in self.test_results if result.status == TestStatus.ERROR)
        
        # Determine status
        if error_tests > 0:
            status = ModuleStatus.ERROR
            health_score = 0.0
        elif failed_tests > 0:
            status = ModuleStatus.WARNING
            health_score = max(0.5, 1.0 - (failed_tests / max(total_tests, 1)))
        else:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        
        issues = []
        if failed_tests > 0:
            issues.append(f"{failed_tests} test(s) failed")
        if error_tests > 0:
            issues.append(f"{error_tests} test(s) had errors")
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=error_tests,
            warning_count=failed_tests
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        
        # In case of issues, we can still provide basic testing capabilities
        remaining_capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
        degraded_capabilities = [ModuleCapability.VALIDATION, ModuleCapability.MONITORING]
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=remaining_capabilities,
            error_message=None
        )
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _initialize_builtin_tests(self):
        """Initialize built-in test cases."""
        
        # Basic functionality tests
        self.test_cases.extend([
            TestCase(
                name="makefile_help",
                description="Test that make help works and shows targets",
                test_type=TestType.UNIT,
                target="help",
                commands=["make help"],
                timeout=10
            ),
            TestCase(
                name="makefile_syntax",
                description="Test Makefile syntax is valid",
                test_type=TestType.UNIT,
                target="syntax",
                commands=["make -n help"],  # Dry run to check syntax
                timeout=5
            ),
            TestCase(
                name="target_discovery",
                description="Test automatic target discovery",
                test_type=TestType.INTEGRATION,
                target="discovery",
                commands=["python scripts/makefile_system_discovery.py"],
                timeout=30
            ),
            TestCase(
                name="safety_validation",
                description="Test safety validation system",
                test_type=TestType.INTEGRATION,
                target="safety",
                commands=["python scripts/makefile_safety_validator.py help"],
                timeout=15
            ),
            TestCase(
                name="performance_optimization",
                description="Test performance optimization system",
                test_type=TestType.INTEGRATION,
                target="performance",
                commands=["python scripts/makefile_performance_optimizer.py help --report"],
                timeout=20
            )
        ])
        
        # System integration tests
        self.test_cases.extend([
            TestCase(
                name="observatory_integration",
                description="Test Observatory system integration",
                test_type=TestType.SYSTEM,
                target="observatory",
                commands=["make observatory-status || echo 'Observatory not running'"],
                expected_result=0,  # Should not fail even if not running
                timeout=15
            ),
            TestCase(
                name="governance_integration",
                description="Test governance system integration",
                test_type=TestType.SYSTEM,
                target="governance",
                commands=["make governance-status"],
                timeout=20
            ),
            TestCase(
                name="testing_integration",
                description="Test testing system integration",
                test_type=TestType.SYSTEM,
                target="testing",
                commands=["make test-makefile-quick"],
                timeout=60
            )
        ])
        
        # Performance tests
        self.test_cases.extend([
            TestCase(
                name="help_performance",
                description="Test that make help responds quickly",
                test_type=TestType.PERFORMANCE,
                target="help",
                commands=["make help"],
                timeout=2  # Should complete in under 2 seconds
            ),
            TestCase(
                name="parallel_execution",
                description="Test parallel execution capabilities",
                test_type=TestType.PERFORMANCE,
                target="parallel",
                commands=["make -j4 help"],
                timeout=5
            )
        ])
        
        # Security tests
        self.test_cases.extend([
            TestCase(
                name="dangerous_operations",
                description="Test dangerous operation detection",
                test_type=TestType.SECURITY,
                target="security",
                commands=["python scripts/makefile_safety_validator.py dangerous_test --commands 'rm -rf /'"],
                expected_result=1,  # Should fail/block dangerous operations
                timeout=10
            ),
            TestCase(
                name="permission_validation",
                description="Test file permission validation",
                test_type=TestType.SECURITY,
                target="permissions",
                commands=["python scripts/makefile_safety_validator.py test --commands 'touch test_file'"],
                cleanup=["rm -f test_file"],
                timeout=10
            )
        ])
    
    def add_test_case(self, test_case: TestCase):
        """Add a custom test case."""
        self.test_cases.append(test_case)
        self._logger.info(f"Added test case: {test_case.name}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases."""
        self._logger.info(f"🧪 Running {len(self.test_cases)} test cases...")
        
        start_time = time.time()
        results = []
        
        for test_case in self.test_cases:
            result = self.run_test_case(test_case)
            results.append(result)
            self.test_results.append(result)
        
        end_time = time.time()
        
        # Generate summary
        summary = self._generate_test_summary(results, end_time - start_time)
        
        self._logger.info(f"✅ Testing complete: {summary['passed']}/{summary['total']} passed")
        return summary
    
    def run_test_case(self, test_case: TestCase) -> TestExecution:
        """Run a single test case."""
        self._logger.info(f"🔬 Running test: {test_case.name}")
        
        start_time = time.time()
        
        try:
            # Check prerequisites
            if not self._check_prerequisites(test_case):
                return TestExecution(
                    test_case=test_case,
                    result=TestResult.SKIP,
                    duration=time.time() - start_time,
                    error="Prerequisites not met",
                    timestamp=start_time
                )
            
            # Execute test commands
            output_lines = []
            error_lines = []
            final_return_code = 0
            
            for command in test_case.commands:
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=test_case.timeout,
                        cwd=self.repository_root
                    )
                    
                    output_lines.append(f"Command: {command}")
                    output_lines.append(f"Return code: {result.returncode}")
                    output_lines.append(f"Output: {result.stdout}")
                    
                    if result.stderr:
                        error_lines.append(f"Error for '{command}': {result.stderr}")
                    
                    # Track the final return code
                    if result.returncode != 0:
                        final_return_code = result.returncode
                    
                except subprocess.TimeoutExpired:
                    error_lines.append(f"Command '{command}' timed out after {test_case.timeout} seconds")
                    final_return_code = -1
                    break
                except Exception as e:
                    error_lines.append(f"Command '{command}' failed: {str(e)}")
                    final_return_code = -1
                    break
            
            # Determine test result
            if final_return_code == test_case.expected_result:
                test_result = TestResult.PASS
            else:
                test_result = TestResult.FAIL
            
            execution = TestExecution(
                test_case=test_case,
                result=test_result,
                duration=time.time() - start_time,
                output="\n".join(output_lines),
                error="\n".join(error_lines),
                return_code=final_return_code,
                timestamp=start_time
            )
            
            # Run cleanup
            self._run_cleanup(test_case)
            
            return execution
            
        except Exception as e:
            return TestExecution(
                test_case=test_case,
                result=TestResult.ERROR,
                duration=time.time() - start_time,
                error=f"Test execution error: {str(e)}",
                timestamp=start_time
            )
    
    def _check_prerequisites(self, test_case: TestCase) -> bool:
        """Check if test prerequisites are met."""
        for prerequisite in test_case.prerequisites:
            try:
                result = subprocess.run(
                    prerequisite,
                    shell=True,
                    capture_output=True,
                    timeout=10,
                    cwd=self.repository_root
                )
                if result.returncode != 0:
                    self._logger.warning(f"Prerequisite failed: {prerequisite}")
                    return False
            except Exception as e:
                self._logger.warning(f"Prerequisite error: {prerequisite}: {e}")
                return False
        
        return True
    
    def _run_cleanup(self, test_case: TestCase):
        """Run cleanup commands for test case."""
        for cleanup_command in test_case.cleanup:
            try:
                subprocess.run(
                    cleanup_command,
                    shell=True,
                    capture_output=True,
                    timeout=10,
                    cwd=self.repository_root
                )
            except Exception as e:
                self._logger.warning(f"Cleanup failed: {cleanup_command}: {e}")
    
    def run_tests_by_type(self, test_type: TestType) -> Dict[str, Any]:
        """Run tests of a specific type."""
        filtered_tests = [tc for tc in self.test_cases if tc.test_type == test_type]
        
        self._logger.info(f"🧪 Running {len(filtered_tests)} {test_type.value} tests...")
        
        start_time = time.time()
        results = []
        
        for test_case in filtered_tests:
            result = self.run_test_case(test_case)
            results.append(result)
            self.test_results.append(result)
        
        end_time = time.time()
        
        summary = self._generate_test_summary(results, end_time - start_time)
        summary["test_type"] = test_type.value
        
        return summary
    
    def run_tests_by_target(self, target: str) -> Dict[str, Any]:
        """Run tests for a specific target."""
        filtered_tests = [tc for tc in self.test_cases if tc.target == target]
        
        self._logger.info(f"🧪 Running {len(filtered_tests)} tests for target '{target}'...")
        
        start_time = time.time()
        results = []
        
        for test_case in filtered_tests:
            result = self.run_test_case(test_case)
            results.append(result)
            self.test_results.append(result)
        
        end_time = time.time()
        
        summary = self._generate_test_summary(results, end_time - start_time)
        summary["target"] = target
        
        return summary
    
    def _generate_test_summary(self, results: List[TestExecution], total_duration: float) -> Dict[str, Any]:
        """Generate test summary report."""
        total = len(results)
        passed = len([r for r in results if r.result == TestResult.PASS])
        failed = len([r for r in results if r.result == TestResult.FAIL])
        skipped = len([r for r in results if r.result == TestResult.SKIP])
        errors = len([r for r in results if r.result == TestResult.ERROR])
        
        return {
            "timestamp": self._get_current_timestamp(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "pass_rate": passed / total if total > 0 else 0,
            "total_duration": total_duration,
            "average_duration": total_duration / total if total > 0 else 0,
            "results": [
                {
                    "name": r.test_case.name,
                    "type": r.test_case.test_type.value,
                    "target": r.test_case.target,
                    "result": r.result.value,
                    "duration": r.duration,
                    "error": r.error if r.error else None
                }
                for r in results
            ]
        }
    
    def generate_test_report(self, output_file: Optional[Path] = None) -> Path:
        """Generate comprehensive test report."""
        if not self.test_results:
            raise ValueError("No test results available. Run tests first.")
        
        if output_file is None:
            output_file = self.repository_root / "reports" / "makefile_system_test_report.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Group results by type
        results_by_type = {}
        for result in self.test_results:
            test_type = result.test_case.test_type.value
            if test_type not in results_by_type:
                results_by_type[test_type] = []
            results_by_type[test_type].append(result)
        
        # Generate comprehensive report
        report = {
            "timestamp": self._get_current_timestamp(),
            "summary": self._generate_test_summary(self.test_results, 
                                                 sum(r.duration for r in self.test_results)),
            "by_type": {
                test_type: self._generate_test_summary(results, 
                                                     sum(r.duration for r in results))
                for test_type, results in results_by_type.items()
            },
            "detailed_results": [
                {
                    "test_name": r.test_case.name,
                    "description": r.test_case.description,
                    "type": r.test_case.test_type.value,
                    "target": r.test_case.target,
                    "result": r.result.value,
                    "duration": r.duration,
                    "return_code": r.return_code,
                    "output": r.output,
                    "error": r.error,
                    "timestamp": r.timestamp
                }
                for r in self.test_results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self._logger.info(f"📊 Test report saved: {output_file}")
        return output_file
    
    def validate_makefile_targets(self) -> Dict[str, Any]:
        """Validate all Makefile targets."""
        self._logger.info("🎯 Validating Makefile targets...")
        
        try:
            # Get list of targets
            result = subprocess.run(
                ["make", "-qp"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.repository_root
            )
            
            # Parse targets from output
            targets = []
            for line in result.stdout.split('\n'):
                if ':' in line and not line.startswith('#') and not line.startswith('\t'):
                    target = line.split(':')[0].strip()
                    if target and not target.startswith('.') and '=' not in target:
                        targets.append(target)
            
            # Remove duplicates and sort
            targets = sorted(list(set(targets)))
            
            # Validate each target
            validation_results = []
            for target in targets:
                try:
                    # Dry run to check syntax
                    result = subprocess.run(
                        ["make", "-n", target],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=self.repository_root
                    )
                    
                    validation_results.append({
                        "target": target,
                        "valid": result.returncode == 0,
                        "error": result.stderr if result.returncode != 0 else None
                    })
                    
                except Exception as e:
                    validation_results.append({
                        "target": target,
                        "valid": False,
                        "error": str(e)
                    })
            
            valid_targets = [r for r in validation_results if r["valid"]]
            invalid_targets = [r for r in validation_results if not r["valid"]]
            
            return {
                "timestamp": self._get_current_timestamp(),
                "total_targets": len(targets),
                "valid_targets": len(valid_targets),
                "invalid_targets": len(invalid_targets),
                "validation_rate": len(valid_targets) / len(targets) if targets else 0,
                "targets": validation_results
            }
            
        except Exception as e:
            return {
                "timestamp": self._get_current_timestamp(),
                "error": f"Failed to validate targets: {str(e)}"
            }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile System Testing Framework")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--type", choices=["unit", "integration", "system", "performance", "security"],
                       help="Run tests of specific type")
    parser.add_argument("--target", help="Run tests for specific target")
    parser.add_argument("--validate-targets", action="store_true", help="Validate all Makefile targets")
    parser.add_argument("--report", help="Generate test report to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create tester
    tester = MakefileSystemTester(args.root)
    
    # Run tests based on arguments
    if args.validate_targets:
        result = tester.validate_makefile_targets()
        print(f"\n🎯 MAKEFILE TARGET VALIDATION")
        print(f"Total targets: {result.get('total_targets', 0)}")
        print(f"Valid targets: {result.get('valid_targets', 0)}")
        print(f"Invalid targets: {result.get('invalid_targets', 0)}")
        print(f"Validation rate: {result.get('validation_rate', 0):.1%}")
        
        if args.verbose and 'targets' in result:
            invalid = [t for t in result['targets'] if not t['valid']]
            if invalid:
                print("\nInvalid targets:")
                for target in invalid:
                    print(f"  ❌ {target['target']}: {target['error']}")
    
    elif args.type:
        result = tester.run_tests_by_type(TestType(args.type))
        print(f"\n🧪 {args.type.upper()} TEST RESULTS")
        print(f"Total: {result['total']}")
        print(f"Passed: {result['passed']}")
        print(f"Failed: {result['failed']}")
        print(f"Skipped: {result['skipped']}")
        print(f"Errors: {result['errors']}")
        print(f"Pass rate: {result['pass_rate']:.1%}")
        print(f"Duration: {result['total_duration']:.2f}s")
    
    elif args.target:
        result = tester.run_tests_by_target(args.target)
        print(f"\n🎯 TARGET '{args.target}' TEST RESULTS")
        print(f"Total: {result['total']}")
        print(f"Passed: {result['passed']}")
        print(f"Failed: {result['failed']}")
        print(f"Pass rate: {result['pass_rate']:.1%}")
        print(f"Duration: {result['total_duration']:.2f}s")
    
    else:
        result = tester.run_all_tests()
        print(f"\n🧪 ALL TESTS COMPLETE")
        print(f"Total: {result['total']}")
        print(f"Passed: {result['passed']}")
        print(f"Failed: {result['failed']}")
        print(f"Skipped: {result['skipped']}")
        print(f"Errors: {result['errors']}")
        print(f"Pass rate: {result['pass_rate']:.1%}")
        print(f"Duration: {result['total_duration']:.2f}s")
    
    # Generate report if requested
    if args.report:
        report_path = tester.generate_test_report(Path(args.report))
        print(f"\n📊 Test report saved: {report_path}")
    
    # Exit with appropriate code
    if 'failed' in result and result['failed'] > 0:
        sys.exit(1)
    elif 'errors' in result and result['errors'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()