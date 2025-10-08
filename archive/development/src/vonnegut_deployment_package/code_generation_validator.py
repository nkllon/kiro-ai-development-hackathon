#!/usr/bin/env python3
"""
Code Generation Validator - Prevents Indentation Issues
======================================================

This script validates generated code to ensure proper class structure and prevent
the indentation issues that caused widespread syntax errors across the codebase.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Prevent future indentation issues from code generation
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of code generation validation."""

    file_path: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


@dataclass
class CodeGenerationReport:
    """Report of code generation validation."""

    total_files: int
    valid_files: int
    invalid_files: int
    error_count: int
    warning_count: int
    validation_results: List[ValidationResult]


class CodeGenerationValidator:
    """Validates generated code for proper structure and syntax."""

    def __init__(self):
        self.validation_rules = {
            "module_level_functions": self._validate_no_module_level_self_functions,
            "class_structure": self._validate_class_structure,
            "import_placement": self._validate_import_placement,
            "method_signatures": self._validate_method_signatures,
            "indentation_consistency": self._validate_indentation_consistency,
        }

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single Python file for code generation issues."""
        errors = []
        warnings = []
        suggestions = []

        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Parse AST to check syntax
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                errors.append(f"Syntax Error: {e.msg} at line {e.lineno}")
                return ValidationResult(
                    file_path=str(file_path),
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    suggestions=suggestions,
                )

            # Apply validation rules
            for rule_name, rule_func in self.validation_rules.items():
                try:
                    rule_result = rule_func(content, lines, tree)
                    errors.extend(rule_result.get("errors", []))
                    warnings.extend(rule_result.get("warnings", []))
                    suggestions.extend(rule_result.get("suggestions", []))
                except Exception as e:
                    errors.append(f"Validation rule '{rule_name}' failed: {str(e)}")

            # Determine overall validity
            is_valid = len(errors) == 0

            return ValidationResult(
                file_path=str(file_path),
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
            )

        except Exception as e:
            return ValidationResult(
                file_path=str(file_path),
                is_valid=False,
                errors=[f"File validation failed: {str(e)}"],
                warnings=warnings,
                suggestions=suggestions,
            )

    def _validate_no_module_level_self_functions(
        self, content: str, lines: List[str], tree: ast.AST
    ) -> Dict[str, List[str]]:
        """Validate that no module-level functions use 'self' parameter."""
        errors = []
        warnings = []
        suggestions = []

        # Find all function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function is at module level (not inside a class)
                parent_is_class = False
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        for child in parent.body:
                            if child == node:
                                parent_is_class = True
                                break
                        if parent_is_class:
                            break

                # If function is at module level and has 'self' parameter
                if not parent_is_class and node.args.args:
                    first_arg = node.args.args[0]
                    if first_arg.arg == "self":
                        errors.append(
                            f"Module-level function '{node.name}' has 'self' parameter at line {node.lineno}"
                        )
                        suggestions.append(
                            f"Wrap function '{node.name}' in a class or remove 'self' parameter"
                        )

        return {"errors": errors, "warnings": warnings, "suggestions": suggestions}

    def _validate_class_structure(
        self, content: str, lines: List[str], tree: ast.AST
    ) -> Dict[str, List[str]]:
        """Validate proper class structure."""
        errors = []
        warnings = []
        suggestions = []

        # Check for classes with proper inheritance
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class has proper docstring
                if (
                    not node.body
                    or not isinstance(node.body[0], ast.Expr)
                    or not isinstance(node.body[0].value, ast.Constant)
                ):
                    warnings.append(
                        f"Class '{node.name}' missing docstring at line {node.lineno}"
                    )
                    suggestions.append(f"Add docstring to class '{node.name}'")

                # Check for __init__ method
                has_init = any(
                    isinstance(child, ast.FunctionDef) and child.name == "__init__"
                    for child in node.body
                )
                if not has_init:
                    warnings.append(f"Class '{node.name}' missing __init__ method")
                    suggestions.append(f"Add __init__ method to class '{node.name}'")

        return {"errors": errors, "warnings": warnings, "suggestions": suggestions}

    def _validate_import_placement(
        self, content: str, lines: List[str], tree: ast.AST
    ) -> Dict[str, List[str]]:
        """Validate that imports are properly placed."""
        errors = []
        warnings = []
        suggestions = []

        # Find all import statements
        import_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                import_lines.append(i + 1)

        # Check if imports are at the top
        non_import_content = False
        for i, line in enumerate(lines):
            if i + 1 in import_lines:
                continue
            if line.strip() and not line.strip().startswith("#"):
                if not non_import_content:
                    non_import_content = True
                else:
                    # Found content after imports, check if there are more imports
                    for j in range(i, len(lines)):
                        if lines[j].strip().startswith(("import ", "from ")):
                            warnings.append(
                                f"Import statement at line {j + 1} should be at top of file"
                            )
                            suggestions.append(
                                "Move all imports to the top of the file"
                            )
                            break

        return {"errors": errors, "warnings": warnings, "suggestions": suggestions}

    def _validate_method_signatures(
        self, content: str, lines: List[str], tree: ast.AST
    ) -> Dict[str, List[str]]:
        """Validate method signatures within classes."""
        errors = []
        warnings = []
        suggestions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        # Check if method has 'self' as first parameter
                        if not child.args.args or child.args.args[0].arg != "self":
                            errors.append(
                                f"Method '{child.name}' in class '{node.name}' missing 'self' parameter at line {child.lineno}"
                            )
                            suggestions.append(
                                f"Add 'self' parameter to method '{child.name}'"
                            )

        return {"errors": errors, "warnings": warnings, "suggestions": suggestions}

    def _validate_indentation_consistency(
        self, content: str, lines: List[str], tree: ast.AST
    ) -> Dict[str, List[str]]:
        """Validate consistent indentation."""
        errors = []
        warnings = []
        suggestions = []

        # Check for mixed tabs and spaces
        has_tabs = any("\t" in line for line in lines)
        has_spaces = any(line.startswith(" ") for line in lines)

        if has_tabs and has_spaces:
            warnings.append("File contains mixed tabs and spaces for indentation")
            suggestions.append("Use consistent indentation (preferably 4 spaces)")

        return {"errors": errors, "warnings": warnings, "suggestions": suggestions}

    def validate_directory(
        self, directory: Path, pattern: str = "*.py"
    ) -> CodeGenerationReport:
        """Validate all Python files in a directory."""
        results = []

        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                result = self.validate_file(file_path)
                results.append(result)

        # Calculate statistics
        total_files = len(results)
        valid_files = sum(1 for r in results if r.is_valid)
        invalid_files = total_files - valid_files
        error_count = sum(len(r.errors) for r in results)
        warning_count = sum(len(r.warnings) for r in results)

        return CodeGenerationReport(
            total_files=total_files,
            valid_files=valid_files,
            invalid_files=invalid_files,
            error_count=error_count,
            warning_count=warning_count,
            validation_results=results,
        )

    def generate_report(self, report: CodeGenerationReport) -> str:
        """Generate a human-readable validation report."""
        report_text = f"""
🔍 CODE GENERATION VALIDATION REPORT
===================================

📊 SUMMARY:
• Total Files: {report.total_files}
• Valid Files: {report.valid_files} ({report.valid_files/report.total_files*100:.1f}%)
• Invalid Files: {report.invalid_files} ({report.invalid_files/report.total_files*100:.1f}%)
• Total Errors: {report.error_count}
• Total Warnings: {report.warning_count}

📋 DETAILED RESULTS:
"""

        for result in report.validation_results:
            if not result.is_valid:
                report_text += f"\n❌ {result.file_path}:\n"
                for error in result.errors:
                    report_text += f"  • ERROR: {error}\n"
                for warning in result.warnings:
                    report_text += f"  • WARNING: {warning}\n"
                for suggestion in result.suggestions:
                    report_text += f"  • SUGGESTION: {suggestion}\n"

        return report_text


def main():
    """Main validation function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate generated code for proper structure"
    )
    parser.add_argument("path", help="Path to file or directory to validate")
    parser.add_argument("--pattern", default="*.py", help="File pattern to match")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    validator = CodeGenerationValidator()
    path = Path(args.path)

    if path.is_file():
        result = validator.validate_file(path)
        report = CodeGenerationReport(
            total_files=1,
            valid_files=1 if result.is_valid else 0,
            invalid_files=0 if result.is_valid else 1,
            error_count=len(result.errors),
            warning_count=len(result.warnings),
            validation_results=[result],
        )
    else:
        report = validator.validate_directory(path, args.pattern)

    # Generate and display report
    report_text = validator.generate_report(report)
    print(report_text)

    # Save report if requested
    if args.output:
        with open(args.output, "w") as f:
            f.write(report_text)
        print(f"Report saved to {args.output}")

    # Exit with error code if validation failed
    if report.invalid_files > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
