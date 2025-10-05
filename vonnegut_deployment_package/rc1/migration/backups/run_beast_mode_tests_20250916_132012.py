#!/usr/bin/env python3
"""
Beast Mode Comprehensive Test Runner

Executes all tests for the components we implemented:
1. Multi-service GCP billing integration
2. PDCA orchestrator critical fixes
3. GKE Terraform configuration validation

Provides systematic test execution with detailed reporting.
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime


class BeastModeTestRunner:
    """Systematic test runner for Beast Mode components"""

    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log_info(self, message):
        """Log info message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ℹ️  {message}")

    def log_success(self, message):
        """Log success message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ✅ {message}")

    def log_error(self, message):
        """Log error message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ {message}")

    def log_warning(self, message):
        """Log warning message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⚠️  {message}")

    def run_test_file(self, test_file, description):
        """Run a specific test file"""
        self.log_info(f"Running {description}...")

        if not Path(test_file).exists():
            self.log_error(f"Test file not found: {test_file}")
            self.test_results[description] = {
                "status": "MISSING",
                "details": "Test file not found",
            }
            return False

        try:
            # Run pytest on the specific file
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    test_file,
                    "-v",
                    "--tb=short",
                    "--no-header",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Parse results
            output = result.stdout + result.stderr

            if result.returncode == 0:
                self.log_success(f"{description} - ALL TESTS PASSED")
                self.test_results[description] = {"status": "PASSED", "output": output}

                # Count passed tests
                passed_count = output.count(" PASSED")
                self.passed_tests += passed_count
                self.total_tests += passed_count

                return True
            else:
                self.log_error(f"{description} - TESTS FAILED")
                self.test_results[description] = {"status": "FAILED", "output": output}

                # Count failed tests
                failed_count = output.count(" FAILED")
                passed_count = output.count(" PASSED")
                self.failed_tests += failed_count
                self.passed_tests += passed_count
                self.total_tests += failed_count + passed_count

                return False

        except subprocess.TimeoutExpired:
            self.log_error(f"{description} - TIMEOUT")
            self.test_results[description] = {
                "status": "TIMEOUT",
                "details": "Test execution timed out",
            }
            return False
        except Exception as e:
            self.log_error(f"{description} - ERROR: {e}")
            self.test_results[description] = {"status": "ERROR", "details": str(e)}
            return False

    def run_direct_test(self, test_script, description):
        """Run a test script directly (not pytest)"""
        self.log_info(f"Running {description}...")

        if not Path(test_script).exists():
            self.log_error(f"Test script not found: {test_script}")
            self.test_results[description] = {
                "status": "MISSING",
                "details": "Test script not found",
            }
            return False

        try:
            result = subprocess.run(
                [sys.executable, test_script],
                capture_output=True,
                text=True,
                timeout=120,
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                self.log_success(f"{description} - VALIDATION PASSED")
                self.test_results[description] = {"status": "PASSED", "output": output}
                self.passed_tests += 1
                self.total_tests += 1
                return True
            else:
                self.log_error(f"{description} - VALIDATION FAILED")
                self.test_results[description] = {"status": "FAILED", "output": output}
                self.failed_tests += 1
                self.total_tests += 1
                return False

        except subprocess.TimeoutExpired:
            self.log_error(f"{description} - TIMEOUT")
            self.test_results[description] = {
                "status": "TIMEOUT",
                "details": "Validation timed out",
            }
            return False
        except Exception as e:
            self.log_error(f"{description} - ERROR: {e}")
            self.test_results[description] = {"status": "ERROR", "details": str(e)}
            return False

    def check_dependencies(self):
        """Check if required dependencies are available"""
        self.log_info("Checking test dependencies...")

        dependencies = {
            "pytest": "pytest testing framework",
            "python": "Python interpreter",
        }

        missing_deps = []

        for dep, description in dependencies.items():
            try:
                if dep == "pytest":
                    subprocess.run(
                        [sys.executable, "-m", "pytest", "--version"],
                        capture_output=True,
                        check=True,
                    )
                elif dep == "python":
                    subprocess.run(
                        [sys.executable, "--version"], capture_output=True, check=True
                    )

                self.log_success(f"{description} - Available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log_warning(f"{description} - Not available")
                missing_deps.append(dep)

        if missing_deps:
            self.log_warning(f"Missing dependencies: {', '.join(missing_deps)}")
            self.log_info("Some tests may be skipped or run with limitations")

        return len(missing_deps) == 0

    def run_all_tests(self):
        """Run all Beast Mode tests systematically"""
        print("🎯 Beast Mode Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Check dependencies
        deps_ok = self.check_dependencies()
        print()

        # Test suite configuration
        test_suite = [
            {
                "file": "tests/integration/test_multi_service_gcp_billing.py",
                "description": "Multi-Service GCP Billing Integration",
                "type": "pytest",
            },
            {
                "file": "tests/integration/test_pdca_orchestrator_fixes.py",
                "description": "PDCA Orchestrator Critical Fixes",
                "type": "pytest",
            },
            {
                "file": "tests/integration/test_gke_terraform_validation.py",
                "description": "GKE Terraform Configuration Validation",
                "type": "pytest",
            },
            {
                "file": "test_multi_service_gcp.py",
                "description": "Multi-Service GCP Live Fire Test",
                "type": "direct",
            },
            {
                "file": "test_pdca_integration.py",
                "description": "PDCA Integration Live Fire Test",
                "type": "direct",
            },
            {
                "file": "validate_gke_config.py",
                "description": "GKE Configuration Validation",
                "type": "direct",
            },
        ]

        # Run tests
        passed_suites = 0
        total_suites = len(test_suite)

        for i, test_config in enumerate(test_suite, 1):
            print(f"\n{'='*60}")
            print(f"Test Suite {i}/{total_suites}: {test_config['description']}")
            print(f"{'='*60}")

            if test_config["type"] == "pytest":
                success = self.run_test_file(
                    test_config["file"], test_config["description"]
                )
            else:
                success = self.run_direct_test(
                    test_config["file"], test_config["description"]
                )

            if success:
                passed_suites += 1

        # Generate summary report
        self.generate_summary_report(passed_suites, total_suites)

        return passed_suites == total_suites

    def generate_summary_report(self, passed_suites, total_suites):
        """Generate comprehensive test summary report"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print(f"\n{'='*60}")
        print("🎉 BEAST MODE TEST EXECUTION SUMMARY")
        print(f"{'='*60}")

        print(f"📊 Overall Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed")
        print(f"   Individual Tests: {self.passed_tests}/{self.total_tests} passed")
        print(
            f"   Success Rate: {(self.passed_tests/max(self.total_tests,1))*100:.1f}%"
        )
        print(f"   Duration: {duration.total_seconds():.1f} seconds")

        print(f"\n📋 Detailed Results:")
        for description, result in self.test_results.items():
            status_emoji = {
                "PASSED": "✅",
                "FAILED": "❌",
                "MISSING": "⚠️",
                "TIMEOUT": "⏰",
                "ERROR": "💥",
            }.get(result["status"], "❓")

            print(f"   {status_emoji} {description}: {result['status']}")

        # Component-specific summary
        print(f"\n🔧 Component Test Results:")

        gcp_tests = [k for k in self.test_results.keys() if "GCP" in k]
        pdca_tests = [k for k in self.test_results.keys() if "PDCA" in k]
        gke_tests = [k for k in self.test_results.keys() if "GKE" in k]

        for component, tests in [
            ("GCP Billing", gcp_tests),
            ("PDCA Orchestrator", pdca_tests),
            ("GKE Infrastructure", gke_tests),
        ]:
            if tests:
                passed = sum(
                    1 for t in tests if self.test_results[t]["status"] == "PASSED"
                )
                total = len(tests)
                status = "✅ PASSED" if passed == total else "❌ ISSUES"
                print(f"   {component}: {passed}/{total} {status}")

        # Systematic superiority assessment
        overall_success = passed_suites == total_suites
        print(f"\n🎯 Systematic Superiority Assessment:")
        if overall_success:
            print("   ✅ SYSTEMATIC APPROACH VALIDATED")
            print("   ✅ All components meet quality standards")
            print("   ✅ Ready for production deployment")
            print("   ✅ Beast Mode effectiveness demonstrated")
        else:
            print("   ⚠️  SYSTEMATIC IMPROVEMENTS NEEDED")
            print("   🔧 Review failed tests and address issues")
            print("   📋 Maintain systematic approach for fixes")

        # Next steps
        print(f"\n🚀 Next Steps:")
        if overall_success:
            print(
                "   1. Deploy GKE infrastructure: cd deployment/gke && PROJECT_ID=your-project ./deploy-gke.sh"
            )
            print("   2. Monitor multi-service GCP costs in real-time")
            print("   3. Execute additional PDCA cycles for continuous improvement")
            print("   4. Proceed with next priority tasks from the DAG")
        else:
            print("   1. Review failed test output for specific issues")
            print("   2. Apply systematic fixes following PDCA methodology")
            print("   3. Re-run tests to validate improvements")
            print("   4. Maintain systematic approach throughout fixes")

        print(f"\n{'='*60}")
        print("Beast Mode Test Execution Complete")
        print(f"{'='*60}")


def main():
    """Main test execution function"""
    runner = BeastModeTestRunner()

    try:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during test execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
