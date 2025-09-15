#!/usr/bin/env python3
"""
Prevention Framework Manager - Comprehensive prevention system
============================================================

This script manages the comprehensive prevention framework to prevent
future indentation issues and maintain code quality.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Manage prevention framework components
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class PreventionComponent:
    """A prevention framework component."""

    name: str
    description: str
    file_path: str
    status: str
    last_validated: Optional[datetime] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreventionReport:
    """Report of prevention framework status."""

    total_components: int
    active_components: int
    failed_components: int
    last_validation: datetime
    components: List[PreventionComponent] = field(default_factory=list)


class PreventionFrameworkManager:
    """Manages the comprehensive prevention framework."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.components = self._initialize_components()

    def _initialize_components(self) -> List[PreventionComponent]:
        """Initialize all prevention framework components."""
        components = [
            PreventionComponent(
                name="Code Generation Validator",
                description="Validates generated code for proper structure",
                file_path="scripts/code_generation_validator.py",
                status="active",
            ),
            PreventionComponent(
                name="Indentation Validator",
                description="Pre-commit hook for indentation consistency",
                file_path="scripts/indentation_validator.py",
                status="active",
            ),
            PreventionComponent(
                name="Code Generation Templates",
                description="Validated templates for safe code generation",
                file_path="scripts/code_generation_templates.py",
                status="active",
            ),
            PreventionComponent(
                name="Pre-commit Configuration",
                description="Pre-commit hooks configuration",
                file_path=".pre-commit-config.yaml",
                status="active",
            ),
            PreventionComponent(
                name="GitHub Actions Workflow",
                description="CI/CD pipeline for syntax validation",
                file_path=".github/workflows/syntax-validation.yml",
                status="active",
            ),
            PreventionComponent(
                name="Integration Test Runner",
                description="Comprehensive integration testing",
                file_path="scripts/integration_test_runner.py",
                status="active",
            ),
            PreventionComponent(
                name="Beast Mode Interface Governance",
                description="Interface duplication prevention",
                file_path="scripts/beast_mode_interface_governance.py",
                status="active",
            ),
        ]

        return components

    def validate_component(self, component: PreventionComponent) -> Dict[str, Any]:
        """Validate a single prevention component."""
        file_path = Path(component.file_path)

        if not file_path.exists():
            return {
                "status": "missing",
                "error": f"File not found: {component.file_path}",
                "suggestion": f"Create missing file: {component.file_path}",
            }

        # Check file syntax if it's a Python file
        if file_path.suffix == ".py":
            try:
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    return {
                        "status": "syntax_error",
                        "error": result.stderr,
                        "suggestion": "Fix syntax errors in the file",
                    }
            except Exception as e:
                return {
                    "status": "validation_error",
                    "error": str(e),
                    "suggestion": "Check file accessibility and permissions",
                }

        # Check YAML syntax for YAML files
        elif file_path.suffix in [".yaml", ".yml"]:
            try:
                import yaml

                with open(file_path, "r") as f:
                    yaml.safe_load(f)
            except Exception as e:
                return {
                    "status": "yaml_error",
                    "error": str(e),
                    "suggestion": "Fix YAML syntax errors",
                }

        return {"status": "valid", "message": "Component is valid and functional"}

    def validate_all_components(self) -> PreventionReport:
        """Validate all prevention framework components."""
        print("🔍 VALIDATING PREVENTION FRAMEWORK COMPONENTS")
        print("=" * 60)

        active_count = 0
        failed_count = 0

        for component in self.components:
            print(f"\n🔍 Validating {component.name}...")

            validation_result = self.validate_component(component)
            component.validation_results = validation_result
            component.last_validated = datetime.now()

            if validation_result["status"] == "valid":
                component.status = "active"
                active_count += 1
                print(f"✅ {component.name}: Valid")
            else:
                component.status = "failed"
                failed_count += 1
                print(f"❌ {component.name}: {validation_result['error']}")

        return PreventionReport(
            total_components=len(self.components),
            active_components=active_count,
            failed_components=failed_count,
            last_validation=datetime.now(),
            components=self.components,
        )

    def install_pre_commit_hooks(self) -> bool:
        """Install pre-commit hooks."""
        try:
            print("🔧 Installing pre-commit hooks...")
            result = subprocess.run(
                ["pre-commit", "install"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                print("✅ Pre-commit hooks installed successfully")
                return True
            else:
                print(f"❌ Failed to install pre-commit hooks: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error installing pre-commit hooks: {e}")
            return False

    def run_pre_commit_validation(self) -> bool:
        """Run pre-commit validation on all files."""
        try:
            print("🔍 Running pre-commit validation...")
            result = subprocess.run(
                ["pre-commit", "run", "--all-files"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("✅ Pre-commit validation passed")
                return True
            else:
                print(f"❌ Pre-commit validation failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error running pre-commit validation: {e}")
            return False

    def generate_prevention_report(self, report: PreventionReport) -> str:
        """Generate comprehensive prevention framework report."""
        report_text = f"""
🛡️ PREVENTION FRAMEWORK STATUS REPORT
====================================

📊 FRAMEWORK STATUS:
• Total Components: {report.total_components}
• Active Components: {report.active_components} ({report.active_components/report.total_components*100:.1f}%)
• Failed Components: {report.failed_components} ({report.failed_components/report.total_components*100:.1f}%)
• Last Validation: {report.last_validation.strftime('%Y-%m-%d %H:%M:%S')}

📋 COMPONENT STATUS:
"""

        for component in report.components:
            status_icon = "✅" if component.status == "active" else "❌"
            report_text += f"{status_icon} {component.name}: {component.description}\n"

            if component.status != "active" and component.validation_results:
                error = component.validation_results.get("error", "Unknown error")
                suggestion = component.validation_results.get(
                    "suggestion", "No suggestion available"
                )
                report_text += f"   Error: {error}\n"
                report_text += f"   Suggestion: {suggestion}\n"

        report_text += f"""
🎯 PREVENTION MEASURES:
• Code Generation Validation: {'✅ Active' if any(c.name == 'Code Generation Validator' and c.status == 'active' for c in report.components) else '❌ Failed'}
• Syntax Checking Hooks: {'✅ Active' if any(c.name == 'Pre-commit Configuration' and c.status == 'active' for c in report.components) else '❌ Failed'}
• Template Review System: {'✅ Active' if any(c.name == 'Code Generation Templates' and c.status == 'active' for c in report.components) else '❌ Failed'}
• Automated Testing Pipeline: {'✅ Active' if any(c.name == 'GitHub Actions Workflow' and c.status == 'active' for c in report.components) else '❌ Failed'}

🔧 RECOMMENDATIONS:
"""

        if report.failed_components > 0:
            report_text += (
                "• Fix failed components to ensure complete prevention coverage\n"
            )
            report_text += "• Re-validate framework after fixes\n"
        else:
            report_text += "• Framework is fully operational\n"
            report_text += "• Continue monitoring and validation\n"

        return report_text

    def setup_prevention_framework(self) -> bool:
        """Set up the complete prevention framework."""
        print("🚀 SETTING UP COMPREHENSIVE PREVENTION FRAMEWORK")
        print("=" * 60)

        # Validate all components
        report = self.validate_all_components()

        if report.failed_components > 0:
            print(f"\n⚠️  {report.failed_components} components failed validation")
            print("Please fix failed components before proceeding")
            return False

        # Install pre-commit hooks
        if not self.install_pre_commit_hooks():
            print("Failed to install pre-commit hooks")
            return False

        # Run initial validation
        if not self.run_pre_commit_validation():
            print("Pre-commit validation failed")
            return False

        print("\n✅ Prevention framework setup complete!")
        return True


def main():
    """Main prevention framework management function."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage prevention framework")
    parser.add_argument(
        "--validate", action="store_true", help="Validate all components"
    )
    parser.add_argument(
        "--setup", action="store_true", help="Set up prevention framework"
    )
    parser.add_argument(
        "--install-hooks", action="store_true", help="Install pre-commit hooks"
    )
    parser.add_argument(
        "--run-validation", action="store_true", help="Run pre-commit validation"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate prevention report"
    )
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    manager = PreventionFrameworkManager()

    if args.validate or args.setup or args.report:
        report = manager.validate_all_components()
        report_text = manager.generate_prevention_report(report)
        print(report_text)

        if args.output:
            with open(args.output, "w") as f:
                f.write(report_text)
            print(f"Report saved to {args.output}")

    if args.setup:
        success = manager.setup_prevention_framework()
        if not success:
            sys.exit(1)

    if args.install_hooks:
        success = manager.install_pre_commit_hooks()
        if not success:
            sys.exit(1)

    if args.run_validation:
        success = manager.run_pre_commit_validation()
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
