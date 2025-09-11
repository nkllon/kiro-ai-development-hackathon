#!/usr/bin/env python3
"""
Comprehensive Integration Test Runner for Beast Mode Agent Collaboration Network

This script runs all comprehensive integration tests and generates a detailed report
validating all requirements from task 13:

- Multi-agent collaboration test scenarios
- End-to-end message flow validation  
- Performance testing for message throughput and latency
- Stress testing for high-volume message scenarios
- Compatibility tests across different platforms

Usage:
    python tests/integration/run_comprehensive_tests.py [options]

Options:
    --performance-only    Run only performance benchmarks
    --compatibility-only  Run only compatibility tests
    --stress-only        Run only stress tests
    --quick              Run quick subset of tests
    --verbose            Verbose output
    --report-file        Output detailed report to file
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import platform

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestSuite:
    """Test suite configuration"""
    
    def __init__(self, name: str, description: str, test_files: List[str], required: bool = True):
        self.name = name
        self.description = description
        self.test_files = test_files
        self.required = required
        self.results = {}
        self.duration = 0
        self.passed = False


class ComprehensiveTestRunner:
    """Comprehensive test runner for Beast Mode integration tests"""
    
    def __init__(self):
        self.test_suites = self._define_test_suites()
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def _define_test_suites(self) -> List[TestSuite]:
        """Define all test suites"""
        return [
            TestSuite(
                name="multi_agent_collaboration",
                description="Multi-agent collaboration scenarios",
                test_files=[
                    "tests/integration/test_comprehensive_beast_mode_integration.py::TestMultiAgentCollaborationScenarios"
                ]
            ),
            TestSuite(
                name="end_to_end_message_flow",
                description="End-to-end message flow validation",
                test_files=[
                    "tests/integration/test_comprehensive_beast_mode_integration.py::TestEndToEndMessageFlowValidation"
                ]
            ),
            TestSuite(
                name="performance_throughput",
                description="Performance and throughput testing",
                test_files=[
                    "tests/integration/test_comprehensive_beast_mode_integration.py::TestPerformanceAndThroughput",
                    "tests/integration/test_performance_benchmarks.py::TestThroughputBenchmarks"
                ]
            ),
            TestSuite(
                name="performance_latency",
                description="Latency performance testing",
                test_files=[
                    "tests/integration/test_performance_benchmarks.py::TestLatencyBenchmarks"
                ]
            ),
            TestSuite(
                name="stress_testing",
                description="Stress testing for high-volume scenarios",
                test_files=[
                    "tests/integration/test_comprehensive_beast_mode_integration.py::TestStressAndVolumeScenarios"
                ]
            ),
            TestSuite(
                name="scalability_testing",
                description="Scalability testing",
                test_files=[
                    "tests/integration/test_performance_benchmarks.py::TestScalabilityBenchmarks"
                ]
            ),
            TestSuite(
                name="cross_platform_compatibility",
                description="Cross-platform compatibility testing",
                test_files=[
                    "tests/integration/test_cross_platform_compatibility.py"
                ]
            ),
            TestSuite(
                name="system_reliability",
                description="System reliability and recovery testing",
                test_files=[
                    "tests/integration/test_comprehensive_beast_mode_integration.py::TestSystemReliabilityAndRecovery",
                    "tests/integration/test_performance_benchmarks.py::TestRecoveryBenchmarks"
                ]
            ),
            TestSuite(
                name="success_criteria_validation",
                description="Success criteria validation",
                test_files=[
                    "tests/integration/test_comprehensive_beast_mode_integration.py::TestSuccessCriteriaValidation"
                ]
            ),
            TestSuite(
                name="existing_integration_tests",
                description="Existing integration test validation",
                test_files=[
                    "tests/integration/test_bus_client.py",
                    "tests/integration/test_agent_discovery.py",
                    "tests/integration/test_help_system_integration.py",
                    "tests/integration/test_mailbox_logger_integration.py",
                    "tests/integration/test_message_routing.py",
                    "tests/integration/test_spore_management_integration.py"
                ],
                required=False
            )
        ]
    
    def run_test_suite(self, suite: TestSuite, verbose: bool = False) -> Dict[str, Any]:
        """Run a single test suite"""
        print(f"\n{'='*60}")
        print(f"Running: {suite.name}")
        print(f"Description: {suite.description}")
        print(f"{'='*60}")
        
        suite_start = time.time()
        suite_results = {
            "name": suite.name,
            "description": suite.description,
            "test_files": suite.test_files,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "duration": 0,
            "passed": False,
            "output": "",
            "errors": []
        }
        
        for test_file in suite.test_files:
            print(f"\nRunning: {test_file}")
            
            # Build pytest command
            cmd = [
                sys.executable, "-m", "pytest",
                test_file,
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header",
                "--json-report",
                "--json-report-file=/tmp/pytest_report.json"
            ]
            
            try:
                # Run the test
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per test file
                )
                
                # Parse results
                try:
                    with open("/tmp/pytest_report.json", "r") as f:
                        pytest_report = json.load(f)
                    
                    suite_results["tests_run"] += pytest_report["summary"]["total"]
                    suite_results["tests_passed"] += pytest_report["summary"]["passed"]
                    suite_results["tests_failed"] += pytest_report["summary"]["failed"]
                    suite_results["tests_skipped"] += pytest_report["summary"]["skipped"]
                    
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    # Fallback to parsing stdout
                    output_lines = result.stdout.split('\n')
                    for line in output_lines:
                        if "passed" in line and "failed" in line:
                            # Try to extract numbers from pytest summary
                            pass
                
                suite_results["output"] += result.stdout
                
                if result.returncode != 0:
                    suite_results["errors"].append({
                        "test_file": test_file,
                        "return_code": result.returncode,
                        "stderr": result.stderr
                    })
                    print(f"❌ FAILED: {test_file}")
                    if verbose:
                        print(f"Error: {result.stderr}")
                else:
                    print(f"✅ PASSED: {test_file}")
                
            except subprocess.TimeoutExpired:
                error_msg = f"Test timeout: {test_file}"
                suite_results["errors"].append({
                    "test_file": test_file,
                    "error": error_msg
                })
                print(f"⏰ TIMEOUT: {test_file}")
                
            except Exception as e:
                error_msg = f"Test execution error: {str(e)}"
                suite_results["errors"].append({
                    "test_file": test_file,
                    "error": error_msg
                })
                print(f"💥 ERROR: {test_file} - {error_msg}")
        
        suite_end = time.time()
        suite_results["duration"] = suite_end - suite_start
        suite_results["passed"] = len(suite_results["errors"]) == 0 and suite_results["tests_failed"] == 0
        
        # Print suite summary
        print(f"\n{suite.name} Summary:")
        print(f"  Tests run: {suite_results['tests_run']}")
        print(f"  Passed: {suite_results['tests_passed']}")
        print(f"  Failed: {suite_results['tests_failed']}")
        print(f"  Skipped: {suite_results['tests_skipped']}")
        print(f"  Duration: {suite_results['duration']:.2f}s")
        print(f"  Status: {'✅ PASSED' if suite_results['passed'] else '❌ FAILED'}")
        
        return suite_results
    
    def run_all_tests(self, 
                     performance_only: bool = False,
                     compatibility_only: bool = False,
                     stress_only: bool = False,
                     quick: bool = False,
                     verbose: bool = False) -> Dict[str, Any]:
        """Run all test suites"""
        
        print("🚀 Beast Mode Agent Collaboration Network - Comprehensive Integration Tests")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print(f"Started: {datetime.now().isoformat()}")
        
        self.start_time = time.time()
        
        # Filter test suites based on options
        suites_to_run = []
        
        if performance_only:
            suites_to_run = [s for s in self.test_suites if "performance" in s.name or "scalability" in s.name]
        elif compatibility_only:
            suites_to_run = [s for s in self.test_suites if "compatibility" in s.name]
        elif stress_only:
            suites_to_run = [s for s in self.test_suites if "stress" in s.name or "scalability" in s.name]
        elif quick:
            # Run only essential tests for quick validation
            suites_to_run = [s for s in self.test_suites if s.name in [
                "multi_agent_collaboration",
                "end_to_end_message_flow",
                "success_criteria_validation"
            ]]
        else:
            suites_to_run = self.test_suites
        
        print(f"\nRunning {len(suites_to_run)} test suites...")
        
        # Run test suites
        all_results = []
        total_passed = 0
        total_failed = 0
        
        for suite in suites_to_run:
            try:
                result = self.run_test_suite(suite, verbose)
                all_results.append(result)
                
                if result["passed"]:
                    total_passed += 1
                else:
                    total_failed += 1
                    
            except KeyboardInterrupt:
                print("\n⚠️  Test execution interrupted by user")
                break
            except Exception as e:
                print(f"\n💥 Unexpected error running {suite.name}: {e}")
                total_failed += 1
        
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        # Generate final report
        final_report = {
            "test_run_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "total_duration": total_duration,
                "platform": platform.system(),
                "python_version": sys.version,
                "test_runner": "Beast Mode Comprehensive Integration Tests"
            },
            "summary": {
                "total_suites": len(suites_to_run),
                "suites_passed": total_passed,
                "suites_failed": total_failed,
                "overall_success": total_failed == 0
            },
            "suite_results": all_results,
            "requirements_validation": self._validate_requirements(all_results)
        }
        
        self._print_final_report(final_report)
        return final_report
    
    def _validate_requirements(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that all task 13 requirements are met"""
        
        requirements = {
            "multi_agent_collaboration_scenarios": False,
            "end_to_end_message_flow_validation": False,
            "performance_throughput_testing": False,
            "performance_latency_testing": False,
            "stress_testing_high_volume": False,
            "compatibility_testing_platforms": False,
            "all_requirements_validation": False
        }
        
        # Check each requirement based on test results
        for result in results:
            if result["passed"]:
                if "multi_agent" in result["name"]:
                    requirements["multi_agent_collaboration_scenarios"] = True
                elif "end_to_end" in result["name"]:
                    requirements["end_to_end_message_flow_validation"] = True
                elif "throughput" in result["name"]:
                    requirements["performance_throughput_testing"] = True
                elif "latency" in result["name"]:
                    requirements["performance_latency_testing"] = True
                elif "stress" in result["name"]:
                    requirements["stress_testing_high_volume"] = True
                elif "compatibility" in result["name"]:
                    requirements["compatibility_testing_platforms"] = True
                elif "success_criteria" in result["name"]:
                    requirements["all_requirements_validation"] = True
        
        # Overall validation
        requirements["task_13_complete"] = all(requirements.values())
        
        return requirements
    
    def _print_final_report(self, report: Dict[str, Any]):
        """Print final test report"""
        
        print(f"\n{'='*80}")
        print("🏁 COMPREHENSIVE INTEGRATION TEST REPORT")
        print(f"{'='*80}")
        
        # Summary
        summary = report["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"  Total test suites: {summary['total_suites']}")
        print(f"  Suites passed: {summary['suites_passed']}")
        print(f"  Suites failed: {summary['suites_failed']}")
        print(f"  Overall success: {'✅ YES' if summary['overall_success'] else '❌ NO'}")
        print(f"  Total duration: {report['test_run_info']['total_duration']:.2f}s")
        
        # Requirements validation
        print(f"\n📋 TASK 13 REQUIREMENTS VALIDATION:")
        req_validation = report["requirements_validation"]
        
        req_items = [
            ("Multi-agent collaboration scenarios", req_validation["multi_agent_collaboration_scenarios"]),
            ("End-to-end message flow validation", req_validation["end_to_end_message_flow_validation"]),
            ("Performance throughput testing", req_validation["performance_throughput_testing"]),
            ("Performance latency testing", req_validation["performance_latency_testing"]),
            ("Stress testing high-volume scenarios", req_validation["stress_testing_high_volume"]),
            ("Compatibility testing across platforms", req_validation["compatibility_testing_platforms"]),
            ("All requirements validation", req_validation["all_requirements_validation"])
        ]
        
        for req_name, req_met in req_items:
            status = "✅ PASSED" if req_met else "❌ FAILED"
            print(f"  {req_name}: {status}")
        
        print(f"\n🎯 TASK 13 COMPLETION: {'✅ COMPLETE' if req_validation['task_13_complete'] else '❌ INCOMPLETE'}")
        
        # Detailed results
        print(f"\n📝 DETAILED RESULTS:")
        for result in report["suite_results"]:
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"  {result['name']}: {status} ({result['duration']:.2f}s)")
            
            if not result["passed"] and result["errors"]:
                for error in result["errors"][:3]:  # Show first 3 errors
                    print(f"    ⚠️  {error.get('test_file', 'Unknown')}: {error.get('error', 'Unknown error')}")
        
        # Performance highlights (if available)
        perf_results = [r for r in report["suite_results"] if "performance" in r["name"]]
        if perf_results:
            print(f"\n⚡ PERFORMANCE HIGHLIGHTS:")
            for result in perf_results:
                if result["passed"]:
                    print(f"  {result['name']}: ✅ All benchmarks passed")
                else:
                    print(f"  {result['name']}: ❌ Some benchmarks failed")
        
        print(f"\n{'='*80}")
        
        if summary["overall_success"]:
            print("🎉 ALL COMPREHENSIVE INTEGRATION TESTS PASSED!")
            print("   Beast Mode Agent Collaboration Network is ready for production!")
        else:
            print("⚠️  SOME TESTS FAILED - Review results above")
            print("   Address failing tests before production deployment")
        
        print(f"{'='*80}")
    
    def save_report(self, report: Dict[str, Any], filename: str):
        """Save detailed report to file"""
        
        report_path = Path(filename)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_path}")


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Comprehensive Integration Test Runner for Beast Mode Agent Collaboration Network"
    )
    
    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="Run only performance benchmarks"
    )
    
    parser.add_argument(
        "--compatibility-only",
        action="store_true",
        help="Run only compatibility tests"
    )
    
    parser.add_argument(
        "--stress-only",
        action="store_true",
        help="Run only stress tests"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick subset of tests"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--report-file",
        type=str,
        default="test_reports/comprehensive_integration_report.json",
        help="Output detailed report to file"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = ComprehensiveTestRunner()
    
    try:
        # Run tests
        report = runner.run_all_tests(
            performance_only=args.performance_only,
            compatibility_only=args.compatibility_only,
            stress_only=args.stress_only,
            quick=args.quick,
            verbose=args.verbose
        )
        
        # Save report
        runner.save_report(report, args.report_file)
        
        # Exit with appropriate code
        exit_code = 0 if report["summary"]["overall_success"] else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()