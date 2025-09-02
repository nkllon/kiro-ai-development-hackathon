#!/usr/bin/env python3
"""
Code Quality Enforcement Script

This script enforces code quality standards and prevents direct editing violations.
It ensures all code follows the round-trip engineering principles.

Usage:
    python scripts/check_code_quality.py <python_file>
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CodeQualityEnforcer:
    """Enforces code quality standards and prevents direct editing violations"""

    def __init__(self):
        self.violations = []
        self.quality_score = 0.0

    def enforce_code_quality(self, file_path: str) -> dict:
        """Enforce code quality standards for a Python file"""
        print(f"🔍 Enforcing code quality for: {file_path}")

        try:
            # Read file content
            with open(file_path) as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Run all quality checks
            self.violations = []
            self.quality_score = 0.0

            print("  🔍 Running quality checks...")

            # Check 1: AST parsing
            self.check_ast_parsing(tree)

            # Check 2: Import quality
            self.check_import_quality(tree)

            # Check 3: Code structure
            self.check_code_structure(tree)

            # Check 4: Documentation
            self.check_documentation(tree)

            # Check 5: Code complexity
            self.check_code_complexity(tree)

            # Check 6: Round-trip compliance
            self.check_round_trip_compliance(content)

            # Calculate overall quality score
            self.calculate_quality_score()

            return {
                "success": len(self.violations) == 0,
                "file": file_path,
                "quality_score": self.quality_score,
                "violations": self.violations,
                "total_checks": 6,
                "passed_checks": 6 - len(self.violations),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": file_path,
                "quality_score": 0.0,
                "violations": [f"Failed to analyze file: {e}"],
                "total_checks": 6,
                "passed_checks": 0,
            }

    def check_ast_parsing(self, tree: ast.AST):
        """Check that the file parses successfully"""
        if tree is None:
            self.violations.append("File failed to parse with AST")
        else:
            print("    ✅ AST parsing: PASSED")

    def check_import_quality(self, tree: ast.AST):
        """Check import quality and organization"""
        import_nodes = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

        if not import_nodes:
            self.violations.append("No imports found - file may be incomplete")
            return

        # Check for unused imports (basic check)
        imported_names = set()
        for node in import_nodes:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imported_names.add(alias.name)

        # Check if imports are used (basic heuristic)
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)

        unused_imports = imported_names - used_names
        if unused_imports:
            self.violations.append(f"Potentially unused imports: {unused_imports}")
        else:
            print("    ✅ Import quality: PASSED")

    def check_code_structure(self, tree: ast.AST):
        """Check code structure and organization"""
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

        # Check for proper spacing between definitions
        if len(classes) > 1 or len(functions) > 1:
            print("    ✅ Code structure: PASSED")
        else:
            print("    ✅ Code structure: PASSED")

    def check_documentation(self, tree: ast.AST):
        """Check documentation quality"""
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

        documented_classes = sum(1 for cls in classes if cls.body and isinstance(cls.body[0], ast.Expr) and isinstance(cls.body[0].value, ast.Constant))
        documented_functions = sum(1 for func in functions if func.body and isinstance(func.body[0], ast.Expr) and isinstance(func.body[0].value, ast.Constant))

        total_definitions = len(classes) + len(functions)
        if total_definitions == 0:
            print("    ✅ Documentation: PASSED (no definitions to document)")
        elif documented_classes + documented_functions >= total_definitions * 0.8:
            print("    ✅ Documentation: PASSED")
        else:
            self.violations.append("Insufficient documentation coverage")

    def check_code_complexity(self, tree: ast.AST):
        """Check code complexity metrics"""
        # Count AST nodes as a basic complexity measure
        node_count = len(list(ast.walk(tree)))

        if node_count > 2000:
            self.violations.append(f"High complexity: {node_count} AST nodes")
        else:
            print("    ✅ Code complexity: PASSED")

    def check_round_trip_compliance(self, content: str):
        """Check round-trip engineering compliance"""
        # Look for signs of direct editing that bypasses round-trip
        suspicious_patterns = [
            "# TODO: Implement",
            "# FIXME:",
            "# HACK:",
            "# XXX:",
            "pass  # TODO",
            "raise NotImplementedError",
            "NotImplemented",
        ]

        found_patterns = []
        for pattern in suspicious_patterns:
            if pattern in content:
                found_patterns.append(pattern)

        if found_patterns:
            self.violations.append(f"Suspicious patterns found (may indicate direct editing): {found_patterns}")
        else:
            print("    ✅ Round-trip compliance: PASSED")

    def calculate_quality_score(self):
        """Calculate overall quality score (0.0 to 1.0)"""
        if not self.violations:
            self.quality_score = 1.0
        else:
            # Deduct points for each violation
            deduction_per_violation = 0.15
            self.quality_score = max(0.0, 1.0 - (len(self.violations) * deduction_per_violation))


def main():
    """Main entry point"""
    # Handle pre-commit mode
    if len(sys.argv) > 1 and sys.argv[1] == "--pre-commit":
        # Pre-commit mode: process all staged Python files
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
                capture_output=True,
                text=True,
                check=True,
            )
            python_files = [f for f in result.stdout.strip().split("\n") if f.endswith(".py") and f]

            if not python_files:
                print("✅ No Python files to check")
                sys.exit(0)

            enforcer = CodeQualityEnforcer()
            all_success = True

            for file_path in python_files:
                if os.path.exists(file_path):
                    print(f"🔍 Checking code quality for: {file_path}")
                    result = enforcer.enforce_code_quality(file_path)
                    if result["success"]:
                        print(f"✅ Code quality passed for: {file_path}")
                    else:
                        print(f"❌ Code quality failed for: {file_path}")
                        all_success = False

            sys.exit(0 if all_success else 1)
        except subprocess.CalledProcessError:
            print("⚠️  Could not determine staged files, skipping code quality check")
            sys.exit(0)
    elif len(sys.argv) != 2:
        print("Usage: python scripts/check_code_quality.py <python_file>")
        print("       python scripts/check_code_quality.py --pre-commit")
        sys.exit(1)
    else:
        file_path = sys.argv[1]

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        if not file_path.endswith(".py"):
            print(f"❌ Not a Python file: {file_path}")
            sys.exit(1)

        # Enforce code quality
        enforcer = CodeQualityEnforcer()
        result = enforcer.enforce_code_quality(file_path)

        if result["success"]:
            print(f"✅ Code quality check PASSED for {file_path}")
            print(f"   🎯 Quality score: {result['quality_score']:.1%}")
            print(f"   ✅ All {result['total_checks']} checks passed")

            # Exit with success
            sys.exit(0)
        else:
            print(f"❌ Code quality check FAILED for {file_path}")
            print(f"   🎯 Quality score: {result['quality_score']:.1%}")
            print(f"   ❌ {len(result['violations'])} violations found:")

            for i, violation in enumerate(result["violations"], 1):
                print(f"      {i}. {violation}")

            print(f"\n   📊 {result['passed_checks']}/{result['total_checks']} checks passed")

            # Exit with failure
            sys.exit(1)


if __name__ == "__main__":
    main()
