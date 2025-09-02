#!/usr/bin/env python3
"""
Reflective Module Compliance Validator

This script validates that all modules in the Round-Trip Engineering system
comply with Reflective Module principles. It's used by the PDCA process
to ensure architectural integrity is maintained.

Usage:
    uv run python scripts/rm_compliance_validator.py [--module <module_name>] [--all]
"""

import ast
import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class ComplianceLevel(Enum):
    """Compliance level enumeration"""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    VIOLATION = "violation"


@dataclass
class ModuleCompliance:
    """Module compliance assessment"""

    module_name: str
    file_path: str
    line_count: int
    size_compliance: ComplianceLevel
    interface_compliance: bool
    single_responsibility: bool
    boundary_compliance: bool
    testability_compliance: bool
    operational_visibility: bool
    overall_compliance: ComplianceLevel
    issues: List[str]
    recommendations: List[str]


class RMComplianceValidator:
    """Validates Reflective Module compliance across the system"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.src_path = self.base_path / "src" / "round_trip_engineering"
        self.compliance_results: List[ModuleCompliance] = []

    def validate_all_modules(self) -> List[ModuleCompliance]:
        """Validate all modules in the round-trip engineering system"""
        print("🔍 Validating Reflective Module Compliance...")
        print(f"📁 Scanning: {self.src_path}")

        # Find all Python files
        python_files = list(self.src_path.rglob("*.py"))
        python_files = [f for f in python_files if not f.name.startswith("__")]

        print(f"📄 Found {len(python_files)} Python modules")

        for file_path in python_files:
            try:
                compliance = self.validate_module(file_path)
                self.compliance_results.append(compliance)
            except Exception as e:
                print(f"❌ Error validating {file_path}: {e}")

        return self.compliance_results

    def validate_module(self, file_path: Path) -> ModuleCompliance:
        """Validate a single module for RM compliance"""
        module_name = self._get_module_name(file_path)
        print(f"  🔍 Validating: {module_name}")

        # Read file content
        with open(file_path, "r") as f:
            content = f.read()

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return ModuleCompliance(
                module_name=module_name,
                file_path=str(file_path),
                line_count=len(content.splitlines()),
                size_compliance=ComplianceLevel.VIOLATION,
                interface_compliance=False,
                single_responsibility=False,
                boundary_compliance=False,
                testability_compliance=False,
                operational_visibility=False,
                overall_compliance=ComplianceLevel.VIOLATION,
                issues=[f"Syntax error: {e}"],
                recommendations=["Fix syntax errors before RM validation"],
            )

        # Assess compliance
        line_count = len(content.splitlines())
        size_compliance = self._assess_size_compliance(line_count)
        interface_compliance = self._assess_interface_compliance(tree, content)
        single_responsibility = self._assess_single_responsibility(tree, content)
        boundary_compliance = self._assess_boundary_compliance(tree, content)
        testability_compliance = self._assess_testability_compliance(tree, content)
        operational_visibility = self._assess_operational_visibility(tree, content)

        # Determine overall compliance
        overall_compliance = self._determine_overall_compliance(
            size_compliance,
            interface_compliance,
            single_responsibility,
            boundary_compliance,
            testability_compliance,
            operational_visibility,
        )

        # Collect issues and recommendations
        issues, recommendations = self._collect_issues_and_recommendations(
            size_compliance,
            interface_compliance,
            single_responsibility,
            boundary_compliance,
            testability_compliance,
            operational_visibility,
            line_count,
        )

        return ModuleCompliance(
            module_name=module_name,
            file_path=str(file_path),
            line_count=line_count,
            size_compliance=size_compliance,
            interface_compliance=interface_compliance,
            single_responsibility=single_responsibility,
            boundary_compliance=boundary_compliance,
            testability_compliance=testability_compliance,
            operational_visibility=operational_visibility,
            overall_compliance=overall_compliance,
            issues=issues,
            recommendations=recommendations,
        )

    def _get_module_name(self, file_path: Path) -> str:
        """Extract module name from file path"""
        relative_path = file_path.relative_to(self.src_path)
        return str(relative_path).replace("/", ".").replace(".py", "")

    def _assess_size_compliance(self, line_count: int) -> ComplianceLevel:
        """Assess module size compliance"""
        if line_count < 100:
            return ComplianceLevel.EXCELLENT
        elif line_count < 150:
            return ComplianceLevel.GOOD
        elif line_count < 200:
            return ComplianceLevel.ACCEPTABLE
        else:
            return ComplianceLevel.VIOLATION

    def _assess_interface_compliance(self, tree: ast.AST, content: str) -> bool:
        """Assess if module implements RM interfaces"""
        required_methods = [
            "get_module_status",
            "get_module_capabilities",
            "is_healthy",
            "get_health_indicators",
        ]

        # Check for class definitions
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for class_node in classes:
            class_methods = [node.name for node in class_node.body if isinstance(node, ast.FunctionDef)]

            # Check if this class implements RM interfaces
            if all(method in class_methods for method in required_methods):
                return True

        # Check if inherits from BaseReflectiveModule
        if "BaseReflectiveModule" in content or "ReflectiveModule" in content:
            return True

        return False

    def _assess_single_responsibility(self, tree: ast.AST, content: str) -> bool:
        """Assess single responsibility principle"""
        # Count different types of operations
        class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])

        # Simple heuristic: if there are many different types of operations,
        # it might violate single responsibility
        if class_count > 3 or function_count > 15:
            return False

        return True

    def _assess_boundary_compliance(self, tree: ast.AST, content: str) -> bool:
        """Assess architectural boundary compliance"""
        # Check for direct attribute access patterns that might indicate boundary violations
        suspicious_patterns = [
            "self._internal_",
            "self.__private_",
            "other_module._internal_",
            "other_module.__private_",
        ]

        for pattern in suspicious_patterns:
            if pattern in content:
                return False

        return True

    def _assess_testability_compliance(self, tree: ast.AST, content: str) -> bool:
        """Assess testability compliance"""
        # Check if module has clear public interfaces
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for class_node in classes:
            public_methods = [node.name for node in class_node.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")]

            if len(public_methods) > 0:
                return True

        return False

    def _assess_operational_visibility(self, tree: ast.AST, content: str) -> bool:
        """Assess operational visibility compliance"""
        # Check for logging, metrics, or status reporting
        visibility_indicators = [
            "logging",
            "logger",
            "print",
            "status",
            "health",
            "metrics",
            "performance",
        ]

        return any(indicator in content for indicator in visibility_indicators)

    def _determine_overall_compliance(self, *compliance_levels) -> ComplianceLevel:
        """Determine overall compliance level"""
        if ComplianceLevel.VIOLATION in compliance_levels:
            return ComplianceLevel.VIOLATION
        elif ComplianceLevel.ACCEPTABLE in compliance_levels:
            return ComplianceLevel.ACCEPTABLE
        elif ComplianceLevel.GOOD in compliance_levels:
            return ComplianceLevel.GOOD
        else:
            return ComplianceLevel.EXCELLENT

    def _collect_issues_and_recommendations(self, *args) -> Tuple[List[str], List[str]]:
        """Collect issues and recommendations based on compliance assessment"""
        issues = []
        recommendations = []

        (
            size_compliance,
            interface_compliance,
            single_responsibility,
            boundary_compliance,
            testability_compliance,
            operational_visibility,
            line_count,
        ) = args

        # Size issues
        if size_compliance == ComplianceLevel.VIOLATION:
            issues.append(f"Module exceeds 200 lines ({line_count} lines)")
            recommendations.append("Refactor into smaller, focused modules")
        elif size_compliance == ComplianceLevel.ACCEPTABLE:
            issues.append(f"Module approaching size limit ({line_count} lines)")
            recommendations.append("Monitor for growth, consider refactoring")

        # Interface issues
        if not interface_compliance:
            issues.append("Missing Reflective Module interface methods")
            recommendations.append("Implement get_module_status, get_module_capabilities, is_healthy, get_health_indicators")

        # Single responsibility issues
        if not single_responsibility:
            issues.append("Module may have multiple responsibilities")
            recommendations.append("Review module purpose, consider splitting into focused modules")

        # Boundary issues
        if not boundary_compliance:
            issues.append("Potential architectural boundary violations")
            recommendations.append("Review module dependencies, ensure clean interfaces")

        # Testability issues
        if not testability_compliance:
            issues.append("Module may not be easily testable")
            recommendations.append("Ensure clear public interfaces for testing")

        # Operational visibility issues
        if not operational_visibility:
            issues.append("Limited operational visibility")
            recommendations.append("Add logging, metrics, or status reporting")

        return issues, recommendations

    def generate_report(self) -> str:
        """Generate comprehensive compliance report"""
        if not self.compliance_results:
            return "No compliance results available"

        report = []
        report.append("🔍 REFLECTIVE MODULE COMPLIANCE REPORT")
        report.append("=" * 50)
        report.append("")

        # Summary statistics
        total_modules = len(self.compliance_results)
        compliant_modules = sum(1 for r in self.compliance_results if r.overall_compliance != ComplianceLevel.VIOLATION)
        excellent_modules = sum(1 for r in self.compliance_results if r.overall_compliance == ComplianceLevel.EXCELLENT)

        report.append(f"📊 SUMMARY")
        report.append(f"  Total Modules: {total_modules}")
        report.append(f"  Compliant: {compliant_modules}/{total_modules} ({compliant_modules/total_modules*100:.1f}%)")
        report.append(f"  Excellent: {excellent_modules}/{total_modules} ({excellent_modules/total_modules*100:.1f}%)")
        report.append("")

        # Detailed results
        for result in self.compliance_results:
            status_emoji = "✅" if result.overall_compliance != ComplianceLevel.VIOLATION else "❌"
            report.append(f"{status_emoji} {result.module_name}")
            report.append(f"   📁 {result.file_path}")
            report.append(f"   📏 Lines: {result.line_count} ({result.size_compliance.value})")
            report.append(f"   🔌 Interfaces: {'✅' if result.interface_compliance else '❌'}")
            report.append(f"   🎯 Single Responsibility: {'✅' if result.single_responsibility else '❌'}")
            report.append(f"   🏗️ Boundaries: {'✅' if result.boundary_compliance else '❌'}")
            report.append(f"   🧪 Testability: {'✅' if result.testability_compliance else '❌'}")
            report.append(f"   👁️ Visibility: {'✅' if result.operational_visibility else '❌'}")
            report.append(f"   📊 Overall: {result.overall_compliance.value.upper()}")

            if result.issues:
                report.append(f"   ⚠️ Issues:")
                for issue in result.issues:
                    report.append(f"     • {issue}")

            if result.recommendations:
                report.append(f"   💡 Recommendations:")
                for rec in result.recommendations:
                    report.append(f"     • {rec}")

            report.append("")

        return "\n".join(report)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Reflective Module compliance")
    parser.add_argument("--module", help="Validate specific module")
    parser.add_argument("--all", action="store_true", help="Validate all modules")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")

    args = parser.parse_args()

    validator = RMComplianceValidator()

    if args.module:
        # Validate specific module
        module_path = Path(f"src/round_trip_engineering/{args.module}.py")
        if module_path.exists():
            result = validator.validate_module(module_path)
            print(f"Module: {result.module_name}")
            print(f"Compliance: {result.overall_compliance.value}")
            if result.issues:
                print("Issues:", result.issues)
        else:
            print(f"Module not found: {module_path}")
    else:
        # Validate all modules
        validator.validate_all_modules()

        if args.report:
            print(validator.generate_report())
        else:
            # Quick summary
            compliant = sum(1 for r in validator.compliance_results if r.overall_compliance != ComplianceLevel.VIOLATION)
            total = len(validator.compliance_results)
            print(f"✅ RM Compliance: {compliant}/{total} modules compliant")


if __name__ == "__main__":
    main()
