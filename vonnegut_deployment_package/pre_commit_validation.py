#!/usr/bin/env python3
"""
Pre-Commit Validation System

Systematic validation that runs before any commit to catch issues like missing modules.
Integrates with git hooks and development workflow.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PreCommitValidator:
    """Comprehensive pre-commit validation system"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.validation_results: Dict[str, Any] = {}
        self.critical_failures: List[str] = []
        self.warnings: List[str] = []

    def run_module_completeness_check(self) -> bool:
        """Run module completeness validation"""
        try:
            logger.info("Running module completeness validation...")
            result = subprocess.run(
                [
                    sys.executable,
                    str(
                        self.project_root
                        / "scripts"
                        / "validate_module_completeness.py"
                    ),
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            success = result.returncode == 0
            self.validation_results["module_completeness"] = {
                "success": success,
                "output": result.stdout,
                "errors": result.stderr,
            }

            if not success:
                self.critical_failures.append("Module completeness validation failed")
                logger.error("Module completeness validation failed")
                print(result.stdout)
                print(result.stderr)

            return success

        except Exception as e:
            logger.error(f"Module completeness check failed: {e}")
            self.critical_failures.append(f"Module completeness check error: {e}")
            return False

    def run_import_tests(self) -> bool:
        """Run comprehensive import tests"""
        try:
            logger.info("Running import tests...")

            # Test critical imports
            critical_imports = [
                "src.competitive_launch.superiority_engine",
                "src.competitive_launch.failure_recovery",
                "src.competitive_launch.launch_execution",
                "src.competitive_launch.intelligence_engine",
                "src.devpost_integration.api_client",
                "src.devpost_integration.auth_service",
                "src.devpost_integration.project_manager",
            ]

            failed_imports = []

            for import_name in critical_imports:
                try:
                    __import__(import_name)
                    logger.info(f"✅ {import_name}")
                except ImportError as e:
                    failed_imports.append(f"{import_name}: {e}")
                    logger.error(f"❌ {import_name}: {e}")

            success = len(failed_imports) == 0
            self.validation_results["import_tests"] = {
                "success": success,
                "failed_imports": failed_imports,
            }

            if not success:
                self.critical_failures.append(f"Import tests failed: {failed_imports}")

            return success

        except Exception as e:
            logger.error(f"Import tests failed: {e}")
            self.critical_failures.append(f"Import tests error: {e}")
            return False

    def run_component_tests(self) -> bool:
        """Run component functionality tests"""
        try:
            logger.info("Running component tests...")

            test_script = """
import sys
sys.path.append('src')

# Test all critical components
components_tested = []
components_failed = []

try:
    from competitive_launch.superiority_engine import SystematicSuperiorityEngine
    engine = SystematicSuperiorityEngine()
    metrics = engine.generate_superiority_metrics()
    components_tested.append('SystematicSuperiorityEngine')
except Exception as e:
    components_failed.append(f'SystematicSuperiorityEngine: {e}')

try:
    from competitive_launch.failure_recovery import FailureRecoverySystem, FailureType
    recovery = FailureRecoverySystem()
    components_tested.append('FailureRecoverySystem')
except Exception as e:
    components_failed.append(f'FailureRecoverySystem: {e}')

try:
    from competitive_launch.launch_execution import LaunchExecutionSystem
    launch = LaunchExecutionSystem()
    components_tested.append('LaunchExecutionSystem')
except Exception as e:
    components_failed.append(f'LaunchExecutionSystem: {e}')

try:
    from competitive_launch.intelligence_engine import CompetitiveIntelligenceEngine
    intelligence = CompetitiveIntelligenceEngine()
    components_tested.append('CompetitiveIntelligenceEngine')
except Exception as e:
    components_failed.append(f'CompetitiveIntelligenceEngine: {e}')

try:
    from devpost_integration.api_client import DevPostAPIClient
    from devpost_integration.auth_service import DevPostAuthService
    from devpost_integration.project_manager import DevpostProjectManager
    components_tested.append('DevPostIntegration')
except Exception as e:
    components_failed.append(f'DevPostIntegration: {e}')

print(f'Components tested: {len(components_tested)}')
print(f'Components failed: {len(components_failed)}')
if components_failed:
    for failure in components_failed:
        print(f'FAILED: {failure}')
    sys.exit(1)
else:
    print('All components working!')
    sys.exit(0)
"""

            result = subprocess.run(
                [sys.executable, "-c", test_script],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            success = result.returncode == 0
            self.validation_results["component_tests"] = {
                "success": success,
                "output": result.stdout,
                "errors": result.stderr,
            }

            if not success:
                self.critical_failures.append("Component tests failed")
                logger.error("Component tests failed")
                print(result.stdout)
                print(result.stderr)

            return success

        except Exception as e:
            logger.error(f"Component tests failed: {e}")
            self.critical_failures.append(f"Component tests error: {e}")
            return False

    def run_quality_checks(self) -> bool:
        """Run code quality checks"""
        try:
            logger.info("Running quality checks...")

            # Check for common issues
            issues = []

            # Check for TODO comments in critical files
            critical_files = [
                "src/competitive_launch/superiority_engine.py",
                "src/competitive_launch/failure_recovery.py",
                "src/competitive_launch/launch_execution.py",
                "src/devpost_integration/auth_service.py",
            ]

            for file_path in critical_files:
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        content = f.read()
                        if "TODO" in content or "FIXME" in content:
                            issues.append(f"TODO/FIXME found in {file_path}")

            # Check for missing docstrings in critical classes
            for file_path in critical_files:
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        content = f.read()
                        if "class " in content and '"""' not in content:
                            issues.append(f"Missing docstrings in {file_path}")

            success = len(issues) == 0
            self.validation_results["quality_checks"] = {
                "success": success,
                "issues": issues,
            }

            if issues:
                self.warnings.extend(issues)
                logger.warning(f"Quality issues found: {issues}")

            return success

        except Exception as e:
            logger.error(f"Quality checks failed: {e}")
            self.critical_failures.append(f"Quality checks error: {e}")
            return False

    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        logger.info("Starting pre-commit validation...")

        validations = [
            ("Module Completeness", self.run_module_completeness_check),
            ("Import Tests", self.run_import_tests),
            ("Component Tests", self.run_component_tests),
            ("Quality Checks", self.run_quality_checks),
        ]

        all_passed = True

        for name, validation_func in validations:
            logger.info(f"Running {name}...")
            try:
                result = validation_func()
                if not result:
                    all_passed = False
                    logger.error(f"{name} failed")
                else:
                    logger.info(f"{name} passed")
            except Exception as e:
                logger.error(f"{name} error: {e}")
                all_passed = False

        return all_passed

    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("🔍 PRE-COMMIT VALIDATION REPORT")
        report.append("=" * 50)

        # Summary
        total_checks = len(self.validation_results)
        passed_checks = sum(
            1
            for result in self.validation_results.values()
            if result.get("success", False)
        )
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        report.append(f"\n📊 SUMMARY:")
        report.append(f"   Total checks: {total_checks}")
        report.append(f"   Passed: {passed_checks}")
        report.append(f"   Failed: {total_checks - passed_checks}")
        report.append(f"   Success rate: {success_rate:.1f}%")

        # Critical failures
        if self.critical_failures:
            report.append(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                report.append(f"   - {failure}")
        else:
            report.append(f"\n✅ NO CRITICAL FAILURES")

        # Warnings
        if self.warnings:
            report.append(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                report.append(f"   - {warning}")
        else:
            report.append(f"\n✅ NO WARNINGS")

        # Overall result
        if success_rate >= 95 and not self.critical_failures:
            report.append(f"\n🏆 OVERALL RESULT: EXCELLENT - Ready to commit")
        elif success_rate >= 90 and not self.critical_failures:
            report.append(f"\n✅ OVERALL RESULT: GOOD - Ready to commit")
        elif not self.critical_failures:
            report.append(f"\n⚠️  OVERALL RESULT: FAIR - Commit with caution")
        else:
            report.append(f"\n❌ OVERALL RESULT: FAILED - Do not commit")

        return "\n".join(report)


def main():
    """Main validation function"""
    validator = PreCommitValidator()
    success = validator.run_all_validations()

    print(validator.generate_report())

    if success:
        print("\n🐺 PRE-COMMIT VALIDATION: PASSED! 💪")
        sys.exit(0)
    else:
        print("\n❌ PRE-COMMIT VALIDATION: FAILED!")
        print("Fix the issues above before committing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
