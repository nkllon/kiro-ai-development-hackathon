#!/usr/bin/env python3
"""
Deterministic F-String Fixer

Purpose: Scan, parse, and fix broken f-strings across the entire codebase
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List


class DeterministicFStringFixer:
    """
    Deterministic tool to fix broken f-strings in Python files
    """

    def __init__(self, workspace_path: str = ".") -> None:
        """Initialize the f-string fixer"""
        self.workspace_path = Path(workspace_path)
        self.fixed_files = []
        self.errors = []

    def scan_workspace(self) -> dict[str, Any]:
        """Scan entire workspace for Python files with f-string issues"""
        print(f"🔍 Scanning workspace: {self.workspace_path}")

        python_files = list(self.workspace_path.rglob("*.py"))
        files_with_issues = []

        for py_file in python_files:
            try:
                issues = self._analyze_file(py_file)
                if issues:
                    files_with_issues.append({"file": str(py_file), "issues": issues})
            except Exception as e:
                self.errors.append(f"Error analyzing {py_file}: {e}")

        return {
            "total_files": len(python_files),
            "files_with_issues": files_with_issues,
            "errors": self.errors,
        }

    def _analyze_file(self, py_file: Path) -> list[dict[str, Any]]:
        """Analyze a single Python file for f-string issues"""
        issues = []

        try:
            content = py_file.read_text()

            # Check for broken f-strings with backslashes
            broken_patterns = [
                (r'f".*\\\\.*"', "f-string with backslash"),
                (r'f".*\n.*"', "f-string with newline"),
                (r'f".*\\s.*"', "f-string with escaped space"),
            ]

            for pattern, description in broken_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    issues.append(
                        {
                            "type": "broken_fstring",
                            "description": description,
                            "line": line_num,
                            "content": match.group(),
                            "pattern": pattern,
                        }
                    )

            # Check if file can be parsed by AST
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(
                    {
                        "type": "syntax_error",
                        "description": f"Syntax error: {e}",
                        "line": e.lineno,
                        "content": str(e),
                        "pattern": "ast_parse_failure",
                    }
                )

        except Exception as e:
            issues.append(
                {
                    "type": "file_error",
                    "description": f"File read error: {e}",
                    "line": 0,
                    "content": str(e),
                    "pattern": "file_read_failure",
                }
            )

        return issues

    def _fix_fstrings_in_content(self, content: str) -> str:
        """Fix broken f-strings in content"""
        fixed_content = content

        # Fix 1: Remove backslashes in f-string expressions
        # Pattern: f"text {expression \n more}" -> f"text {expression} more"
        pattern1 = r'f"([^"]*?)\{([^}]*?)\\\\(\s*)([^"]*?)"'
        replacement1 = r'f"\1{\2}\3\4"'
        fixed_content = re.sub(pattern1, replacement1, fixed_content)

        # Fix 2: Fix multi-line f-strings with backslashes
        # Pattern: f"text {expression \n    more}" -> f"text {expression} more"
        pattern2 = r'f"([^"]*?)\{([^}]*?)\\\\(\s*)\n(\s*)([^"]*?)"'
        replacement2 = r'f"\1{\2}\3\4\5"'
        fixed_content = re.sub(pattern2, replacement2, fixed_content)

        # Fix 3: Remove redundant backslashes between brackets
        # Pattern: f"text {len(\n    data)}" -> f"text {len(data)}"
        pattern3 = r'f"([^"]*?)\{([^}]*?)\\\\(\s*)\n(\s*)([^}]*?)\}'
        replacement3 = r'f"\1{\2}\3\4\5}'
        return re.sub(pattern3, replacement3, fixed_content)

    def _save_fixed_file(self, py_file: Path, fixed_content: str) -> bool:
        """Save the fixed content back to the file"""
        try:
            # Validate that the fixed content parses
            ast.parse(fixed_content)

            # Backup original file
            backup_path = py_file.with_suffix(".py.backup")
            py_file.rename(backup_path)

            # Write fixed content
            py_file.write_text(fixed_content)

            # Verify the fix worked
            try:
                ast.parse(py_file.read_text())
                self.fixed_files.append(str(py_file))
                return True
            except SyntaxError:
                # Restore backup if fix failed
                py_file.unlink()
                backup_path.rename(py_file)
                return False

        except Exception as e:
            self.errors.append(f"Error saving {py_file}: {e}")
            return False

    def fix_file(self, file_path: str) -> bool:
        """Fix f-string issues in a specific file"""
        py_file = Path(file_path)
        if not py_file.exists():
            print(f"❌ File not found: {file_path}")
            return False

        print(f"🔧 Fixing f-string issues in: {file_path}")

        try:
            # Analyze the file
            issues = self._analyze_file(py_file)
            if not issues:
                print(f"✅ No f-string issues found in {file_path}")
                return True

            print(f"🚨 Found {len(issues)} issues in {file_path}")

            # Read and fix content
            content = py_file.read_text()
            fixed_content = self._fix_fstrings_in_content(content)

            # Save fixed file
            if self._save_fixed_file(py_file, fixed_content):
                print(f"✅ Successfully fixed {file_path}")
                return True
            print(f"❌ Failed to fix {file_path}")
            return False

        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            return False

    def generate_report(self) -> str:
        """Generate a report of the fixing operation"""
        report = f"""
🔧 F-String Fixer Report
========================

📁 Workspace: {self.workspace_path}
✅ Files Fixed: {len(self.fixed_files)}
❌ Errors: {len(self.errors)}

📋 Fixed Files:
"""

        for file_path in self.fixed_files:
            report += f"  ✅ {file_path}\n"

        if self.errors:
            report += f"\n🚨 Errors:\n"
            for error in self.errors:
                report += f"  ❌ {error}\n"

        return report

    def validate_fixes(self) -> bool:
        """Validate that all fixed files now parse correctly"""
        print("🔍 Validating fixes...")

        all_valid = True
        for file_path in self.fixed_files:
            try:
                with open(file_path) as f:
                    content = f.read()
                ast.parse(content)
                print(f"✅ {file_path} parses correctly")
            except SyntaxError as e:
                print(f"❌ {file_path} still has syntax errors: {e}")
                all_valid = False

        return all_valid


def main() -> None:
    """Main entry point for Deterministic F-String Fixer"""
    import sys

    print("🚀 Deterministic F-String Fixer")

    if len(sys.argv) < 2:
        print("Usage: python deterministic_fstring_fixer.py <file_path>")
        print("   or: python deterministic_fstring_fixer.py --scan")
        return

    fixer = DeterministicFStringFixer()

    if sys.argv[1] == "--scan":
        # Scan entire workspace
        results = fixer.scan_workspace()
        print("📊 Scan Results:")
        print(f"  Total Python files: {results['total_files']}")
        print(f"  Files with issues: {len(results['files_with_issues'])}")
        print(f"  Errors: {len(results['errors'])}")

        if results["files_with_issues"]:
            print("\n🚨 Files with f-string issues:")
            for file_info in results["files_with_issues"]:
                print(f"  {file_info['file']}: {len(file_info['issues'])} issues")
    else:
        # Fix specific file
        file_path = sys.argv[1]
        success = fixer.fix_file(file_path)

        if success:
            print(f"✅ Successfully fixed {file_path}")

            # Validate the fix
            if fixer.validate_fixes():
                print("✅ All fixes validated successfully!")
            else:
                print("❌ Some fixes failed validation")
        else:
            print(f"❌ Failed to fix {file_path}")

    # Generate report
    print(fixer.generate_report())


if __name__ == "__main__":
    main()
