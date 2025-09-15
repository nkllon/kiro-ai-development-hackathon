#!/usr/bin/env python3
"""
Indentation Validator - Pre-commit hook for indentation consistency
===============================================================

This script validates indentation consistency and prevents the specific
indentation issues that caused widespread syntax errors.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Pre-commit validation for indentation consistency
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any


class IndentationValidator:
    """Validates indentation consistency in Python files."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate indentation in a single file."""
        errors = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Check 1: Mixed tabs and spaces
            has_tabs = any("\t" in line for line in lines)
            has_spaces = any(
                line.startswith(" ") or line.startswith("\t")
                for line in lines
                if line.strip()
            )

            if has_tabs:
                # Check for mixed indentation
                for i, line in enumerate(lines):
                    if line.strip() and (
                        "\t" in line and " " in line[: len(line) - len(line.lstrip())]
                    ):
                        errors.append(
                            f"Line {i+1}: Mixed tabs and spaces in indentation"
                        )

            # Check 2: Inconsistent indentation levels
            indent_levels = set()
            for line in lines:
                if line.strip():
                    leading_whitespace = line[: len(line) - len(line.lstrip())]
                    if leading_whitespace:
                        indent_levels.add(len(leading_whitespace))

            # Check 3: Validate AST parsing
            try:
                ast.parse(content)
            except SyntaxError as e:
                if "unexpected indent" in str(e):
                    errors.append(f"Syntax Error: {e.msg} at line {e.lineno}")
                elif "unindent does not match any outer indentation level" in str(e):
                    errors.append(f"Indentation Error: {e.msg} at line {e.lineno}")
                else:
                    errors.append(f"Syntax Error: {e.msg} at line {e.lineno}")

            # Check 4: Module-level functions with 'self' parameter
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function is at module level
                        parent_is_class = False
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.ClassDef):
                                for child in parent.body:
                                    if child == node:
                                        parent_is_class = True
                                        break
                                if parent_is_class:
                                    break

                        # If module-level function has 'self' parameter
                        if (
                            not parent_is_class
                            and node.args.args
                            and node.args.args[0].arg == "self"
                        ):
                            errors.append(
                                f"Line {node.lineno}: Module-level function '{node.name}' has 'self' parameter"
                            )
            except SyntaxError:
                pass  # Already handled above

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Validation failed: {str(e)}"]

    def validate_files(self, file_paths: List[str]) -> bool:
        """Validate multiple files."""
        all_valid = True

        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            if not file_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue

            if not file_path.suffix == ".py":
                continue

            is_valid, errors = self.validate_file(file_path)

            if not is_valid:
                all_valid = False
                print(f"❌ {file_path}:")
                for error in errors:
                    print(f"  • {error}")
            else:
                print(f"✅ {file_path}: Valid indentation")

        return all_valid


def main():
    """Main function for pre-commit hook."""
    if len(sys.argv) < 2:
        print("Usage: python3 indentation_validator.py <file1> [file2] ...")
        sys.exit(1)

    validator = IndentationValidator()
    file_paths = sys.argv[1:]

    is_valid = validator.validate_files(file_paths)

    if not is_valid:
        print("\n🚨 Indentation validation failed!")
        print("Please fix the indentation issues before committing.")
        sys.exit(1)
    else:
        print("\n✅ All files passed indentation validation!")


if __name__ == "__main__":
    main()
