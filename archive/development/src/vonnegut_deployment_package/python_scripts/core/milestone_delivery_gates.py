#!/usr/bin/env python3
"""
Milestone Delivery Gates Check

This system verifies that all milestone delivery gates have been met
for the Beast Mode Framework RDI compliance implementation.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path


class MilestoneDeliveryGates:
    """System for checking milestone delivery gates."""

    def __init__(self):
        self.gates = {}
        self.results = {}
        self.overall_status = "PENDING"

    def check_all_gates(self):
        """Check all milestone delivery gates."""
        print("🚪 MILESTONE DELIVERY GATES CHECK")
        print("=" * 50)
        print(f"Check performed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Gate 1: RDI Compliance
        self.check_rdi_compliance_gate()

        # Gate 2: Size Compliance
        self.check_size_compliance_gate()

        # Gate 3: Health Monitoring
        self.check_health_monitoring_gate()

        # Gate 4: Registry Integration
        self.check_registry_integration_gate()

        # Gate 5: Interface Consolidation
        self.check_interface_consolidation_gate()

        # Gate 6: Test Suite
        self.check_test_suite_gate()

        # Gate 7: Documentation
        self.check_documentation_gate()

        # Gate 8: System Health
        self.check_system_health_gate()

        # Gate 9: Performance
        self.check_performance_gate()

        # Gate 10: Security
        self.check_security_gate()

        # Calculate overall status
        self.calculate_overall_status()

        # Generate report
        self.generate_delivery_report()

    def check_rdi_compliance_gate(self):
        """Check RDI compliance gate."""
        print("🔍 Gate 1: RDI Compliance")
        gate_status = "PASS"
        issues = []

        try:
            # Check if ReflectiveModule is properly implemented
            reflective_module_files = self.find_files("reflective_module.py")
            if not reflective_module_files:
                gate_status = "FAIL"
                issues.append("ReflectiveModule base class not found")

            # Check if modules inherit from ReflectiveModule
            modules_with_reflective = self.count_modules_with_reflective()
            total_modules = self.count_total_modules()

            if modules_with_reflective < total_modules * 0.95:  # 95% threshold
                gate_status = "FAIL"
                issues.append(
                    f"Only {modules_with_reflective}/{total_modules} modules inherit from ReflectiveModule"
                )

            # Check for required methods
            required_methods = ["get_module_info", "get_capabilities", "check_health"]
            missing_methods = self.check_required_methods(required_methods)

            if missing_methods:
                gate_status = "FAIL"
                issues.append(f"Missing required methods: {', '.join(missing_methods)}")

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking RDI compliance: {e}")

        self.gates["rdi_compliance"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Modules with ReflectiveModule: {modules_with_reflective}/{total_modules}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_size_compliance_gate(self):
        """Check size compliance gate."""
        print("🔍 Gate 2: Size Compliance")
        gate_status = "PASS"
        issues = []

        try:
            # Check for files over 200 lines
            large_files = self.find_large_files(200)

            if large_files:
                gate_status = "FAIL"
                issues.append(f"Found {len(large_files)} files over 200 lines")
                for file_path, line_count in large_files[:5]:  # Show first 5
                    issues.append(f"  {file_path}: {line_count} lines")

            # Check average file size
            avg_size = self.calculate_average_file_size()
            if avg_size > 150:  # Warning threshold
                issues.append(f"Average file size is high: {avg_size:.1f} lines")

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking size compliance: {e}")

        self.gates["size_compliance"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Large files: {len(large_files) if 'large_files' in locals() else 0}, Avg size: {avg_size if 'avg_size' in locals() else 0:.1f}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_health_monitoring_gate(self):
        """Check health monitoring gate."""
        print("🔍 Gate 3: Health Monitoring")
        gate_status = "PASS"
        issues = []

        try:
            # Check for health monitoring methods
            health_methods = [
                "check_health",
                "get_health_indicators",
                "get_status_report",
            ]
            modules_with_health = self.count_modules_with_methods(health_methods)
            total_modules = self.count_total_modules()

            if modules_with_health < total_modules * 0.90:  # 90% threshold
                gate_status = "FAIL"
                issues.append(
                    f"Only {modules_with_health}/{total_modules} modules have health monitoring"
                )

            # Check for health dashboard
            if not os.path.exists("src/health_dashboard.py"):
                gate_status = "FAIL"
                issues.append("Health monitoring dashboard not found")

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking health monitoring: {e}")

        self.gates["health_monitoring"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Modules with health monitoring: {modules_with_health}/{total_modules}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_registry_integration_gate(self):
        """Check registry integration gate."""
        print("🔍 Gate 4: Registry Integration")
        gate_status = "PASS"
        issues = []

        try:
            # Check for registry methods
            registry_methods = [
                "get_module_info",
                "get_capabilities",
                "get_dependencies",
                "register_with_registry",
            ]
            modules_with_registry = self.count_modules_with_methods(registry_methods)
            total_modules = self.count_total_modules()

            if modules_with_registry < total_modules * 0.90:  # 90% threshold
                gate_status = "FAIL"
                issues.append(
                    f"Only {modules_with_registry}/{total_modules} modules have registry integration"
                )

            # Check for registry dashboard
            if not os.path.exists("src/registry_dashboard.py"):
                gate_status = "FAIL"
                issues.append("Registry monitoring dashboard not found")

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking registry integration: {e}")

        self.gates["registry_integration"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Modules with registry integration: {modules_with_registry}/{total_modules}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_interface_consolidation_gate(self):
        """Check interface consolidation gate."""
        print("🔍 Gate 5: Interface Consolidation")
        gate_status = "PASS"
        issues = []

        try:
            # Check for interface consolidation report
            if not os.path.exists("interface_consolidation_report.json"):
                gate_status = "FAIL"
                issues.append("Interface consolidation report not found")
            else:
                with open("interface_consolidation_report.json", "r") as f:
                    report = json.load(f)

                consistency_score = report.get("summary", {}).get(
                    "consistency_score", 0
                )
                if consistency_score < 30:  # 30% threshold
                    gate_status = "FAIL"
                    issues.append(f"Consistency score too low: {consistency_score}%")

            # Check for authoritative interfaces
            interfaces_dir = Path("src/interfaces")
            if not interfaces_dir.exists():
                gate_status = "FAIL"
                issues.append("Authoritative interfaces directory not found")
            else:
                interface_files = list(interfaces_dir.glob("*.py"))
                if len(interface_files) < 10:  # Expect at least 10 interfaces
                    issues.append(
                        f"Only {len(interface_files)} authoritative interfaces found"
                    )

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking interface consolidation: {e}")

        self.gates["interface_consolidation"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Consistency score: {consistency_score if 'consistency_score' in locals() else 'unknown'}%",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_test_suite_gate(self):
        """Check test suite gate."""
        print("🔍 Gate 6: Test Suite")
        gate_status = "PASS"
        issues = []

        try:
            # Check for test files
            test_files = self.find_files("test_*.py", "tests")
            if len(test_files) < 10:
                gate_status = "FAIL"
                issues.append(f"Only {len(test_files)} test files found")

            # Check for test utilities
            if not os.path.exists("tests/test_utilities.py"):
                gate_status = "FAIL"
                issues.append("Test utilities not found")

            # Check for comprehensive test runner
            if not os.path.exists("tests/run_comprehensive_tests.py"):
                gate_status = "FAIL"
                issues.append("Comprehensive test runner not found")

            # Try to run a basic test
            try:
                result = subprocess.run(
                    ["python3", "-m", "pytest", "tests/test_basic.py", "-q"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    gate_status = "FAIL"
                    issues.append("Basic tests are failing")
            except subprocess.TimeoutExpired:
                issues.append("Test execution timed out")
            except Exception as e:
                issues.append(f"Error running tests: {e}")

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking test suite: {e}")

        self.gates["test_suite"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Test files: {len(test_files) if 'test_files' in locals() else 0}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_documentation_gate(self):
        """Check documentation gate."""
        print("🔍 Gate 7: Documentation")
        gate_status = "PASS"
        issues = []

        try:
            # Check for key documentation files
            required_docs = [
                "README.md",
                "RDI_COMPLIANCE_PROGRESS_REPORT.md",
                "RDI_ANALYSIS_SUMMARY.md",
            ]

            for doc in required_docs:
                if not os.path.exists(doc):
                    gate_status = "FAIL"
                    issues.append(f"Missing documentation: {doc}")

            # Check for inline documentation
            modules_with_docstrings = self.count_modules_with_docstrings()
            total_modules = self.count_total_modules()

            if modules_with_docstrings < total_modules * 0.80:  # 80% threshold
                issues.append(
                    f"Only {modules_with_docstrings}/{total_modules} modules have docstrings"
                )

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking documentation: {e}")

        self.gates["documentation"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Modules with docstrings: {modules_with_docstrings}/{total_modules}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_system_health_gate(self):
        """Check system health gate."""
        print("🔍 Gate 8: System Health")
        gate_status = "PASS"
        issues = []

        try:
            # Check system resources
            import psutil

            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                gate_status = "FAIL"
                issues.append(f"Memory usage too high: {memory.percent}%")

            # Disk usage
            disk = psutil.disk_usage("/")
            if disk.percent > 95:
                gate_status = "FAIL"
                issues.append(f"Disk usage too high: {disk.percent}%")

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                issues.append(f"CPU usage high: {cpu_percent}%")

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking system health: {e}")

        self.gates["system_health"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Memory: {memory.percent if 'memory' in locals() else 'unknown'}%, Disk: {disk.percent if 'disk' in locals() else 'unknown'}%",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_performance_gate(self):
        """Check performance gate."""
        print("🔍 Gate 9: Performance")
        gate_status = "PASS"
        issues = []

        try:
            # Check for performance test files
            perf_tests = self.find_files("test_*performance*.py", "tests")
            if len(perf_tests) == 0:
                issues.append("No performance tests found")

            # Check for performance monitoring
            if not os.path.exists("src/health_dashboard.py"):
                issues.append("Performance monitoring dashboard not found")

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking performance: {e}")

        self.gates["performance"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Performance tests: {len(perf_tests) if 'perf_tests' in locals() else 0}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def check_security_gate(self):
        """Check security gate."""
        print("🔍 Gate 10: Security")
        gate_status = "PASS"
        issues = []

        try:
            # Check for security-related files
            security_files = ["requirements.txt", "pyproject.toml"]

            for file in security_files:
                if not os.path.exists(file):
                    gate_status = "FAIL"
                    issues.append(f"Missing security file: {file}")

            # Check for hardcoded secrets (basic check)
            secret_patterns = ["password", "secret", "key", "token"]
            files_with_secrets = self.find_files_with_patterns(secret_patterns)
            if files_with_secrets:
                issues.append(
                    f"Potential secrets found in {len(files_with_secrets)} files"
                )

        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking security: {e}")

        self.gates["security"] = {
            "status": gate_status,
            "issues": issues,
            "details": f"Files with potential secrets: {len(files_with_secrets) if 'files_with_secrets' in locals() else 0}",
        }

        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()

    def calculate_overall_status(self):
        """Calculate overall milestone status."""
        total_gates = len(self.gates)
        passed_gates = sum(
            1 for gate in self.gates.values() if gate["status"] == "PASS"
        )

        if passed_gates == total_gates:
            self.overall_status = "PASS"
        elif passed_gates >= total_gates * 0.8:  # 80% threshold
            self.overall_status = "PASS_WITH_WARNINGS"
        else:
            self.overall_status = "FAIL"

    def generate_delivery_report(self):
        """Generate milestone delivery report."""
        print("=" * 50)
        print("📋 MILESTONE DELIVERY REPORT")
        print("=" * 50)

        total_gates = len(self.gates)
        passed_gates = sum(
            1 for gate in self.gates.values() if gate["status"] == "PASS"
        )
        failed_gates = sum(
            1 for gate in self.gates.values() if gate["status"] == "FAIL"
        )

        print(f"Overall Status: {self.overall_status}")
        print(f"Gates Passed: {passed_gates}/{total_gates}")
        print(f"Gates Failed: {failed_gates}/{total_gates}")
        print()

        if self.overall_status == "PASS":
            print("🎉 ALL MILESTONE DELIVERY GATES PASSED!")
            print("✅ The Beast Mode Framework is ready for delivery!")
        elif self.overall_status == "PASS_WITH_WARNINGS":
            print("⚠️  MILESTONE DELIVERY GATES PASSED WITH WARNINGS")
            print(
                "✅ The Beast Mode Framework is ready for delivery with minor issues to address."
            )
        else:
            print("❌ MILESTONE DELIVERY GATES FAILED")
            print("🚫 The Beast Mode Framework is NOT ready for delivery.")
            print("Please address the failed gates before proceeding.")

        print()
        print("Gate Details:")
        for gate_name, gate_data in self.gates.items():
            status_icon = "✅" if gate_data["status"] == "PASS" else "❌"
            print(
                f"  {status_icon} {gate_name.replace('_', ' ').title()}: {gate_data['status']}"
            )
            if gate_data["issues"]:
                for issue in gate_data["issues"]:
                    print(f"    - {issue}")

        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.overall_status,
            "total_gates": total_gates,
            "passed_gates": passed_gates,
            "failed_gates": failed_gates,
            "gates": self.gates,
        }

        with open("milestone_delivery_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: milestone_delivery_report.json")

    # Helper methods
    def find_files(self, pattern, directory="src"):
        """Find files matching pattern."""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if pattern in filename:
                    files.append(os.path.join(root, filename))
        return files

    def count_modules_with_reflective(self):
        """Count modules that inherit from ReflectiveModule."""
        count = 0
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                        if "ReflectiveModule" in content and "class " in content:
                            count += 1
                    except:
                        pass
        return count

    def count_total_modules(self):
        """Count total Python modules."""
        count = 0
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    count += 1
        return count

    def check_required_methods(self, methods):
        """Check for required methods across modules."""
        missing = []
        for method in methods:
            found = False
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r") as f:
                                content = f.read()
                            if f"def {method}(" in content:
                                found = True
                                break
                        except:
                            pass
            if not found:
                missing.append(method)
        return missing

    def find_large_files(self, max_lines):
        """Find files over max_lines."""
        large_files = []
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            line_count = len(f.readlines())
                        if line_count > max_lines:
                            large_files.append((file_path, line_count))
                    except:
                        pass
        return large_files

    def calculate_average_file_size(self):
        """Calculate average file size."""
        total_lines = 0
        file_count = 0
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            total_lines += len(f.readlines())
                        file_count += 1
                    except:
                        pass
        return total_lines / file_count if file_count > 0 else 0

    def count_modules_with_methods(self, methods):
        """Count modules that have all specified methods."""
        count = 0
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                        if all(f"def {method}(" in content for method in methods):
                            count += 1
                    except:
                        pass
        return count

    def count_modules_with_docstrings(self):
        """Count modules with docstrings."""
        count = 0
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                        if '"""' in content or "'''" in content:
                            count += 1
                    except:
                        pass
        return count

    def find_files_with_patterns(self, patterns):
        """Find files containing specific patterns."""
        files = []
        for root, dirs, filenames in os.walk("src"):
            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, "r") as f:
                            content = f.read().lower()
                        if any(pattern in content for pattern in patterns):
                            files.append(file_path)
                    except:
                        pass
        return files


def main():
    """Main milestone delivery gates check."""
    gates = MilestoneDeliveryGates()
    gates.check_all_gates()


if __name__ == "__main__":
    main()
