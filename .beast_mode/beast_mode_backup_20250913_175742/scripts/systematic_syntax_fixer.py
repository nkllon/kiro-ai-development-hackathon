#!/usr/bin/env python3
"""
🔧 SYSTEMATIC SYNTAX FIXER
=========================
Systematically fix the 222 syntax errors identified in the RCA.
"""

import os
import sys
import ast
import json
import shutil
from datetime import datetime
from pathlib import Path


class SystematicSyntaxFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = 0
        self.errors_fixed = 0
        self.backup_created = False

    def create_emergency_backup(self):
        """Create emergency backup before fixing"""
        print("📦 Creating emergency backup...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f".beast_mode/emergency_backup_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup src directory
        if os.path.exists("src"):
            shutil.copytree("src", backup_dir / "src")

        # Backup scripts
        if os.path.exists("scripts"):
            shutil.copytree("scripts", backup_dir / "scripts")

        print(f"   ✅ Emergency backup created: {backup_dir}")
        self.backup_created = True
        return str(backup_dir)

    def identify_syntax_errors(self):
        """Identify all syntax errors systematically"""
        print("🔍 Identifying syntax errors...")

        syntax_errors = []
        total_files = 0

        for py_file in self.project_root.rglob("src/**/*.py"):
            total_files += 1
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append(
                    {
                        "file": str(py_file),
                        "error": str(e),
                        "line": e.lineno if hasattr(e, "lineno") else None,
                        "text": e.text if hasattr(e, "text") else None,
                    }
                )
            except Exception as e:
                syntax_errors.append(
                    {"file": str(py_file), "error": str(e), "line": None, "text": None}
                )

        print(f"   📊 Found {len(syntax_errors)} syntax errors in {total_files} files")
        return syntax_errors

    def fix_common_syntax_errors(self, file_path, error_info):
        """Apply common syntax fixes"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            original_lines = lines.copy()
            fixed = False

            # Fix common patterns
            error_msg = error_info["error"].lower()

            if "expected an indented block" in error_msg:
                # Add pass statement for empty blocks
                error_line = error_info["line"] - 1 if error_info["line"] else 0
                if error_line < len(lines):
                    # Find the end of the current block and add pass
                    indent = len(lines[error_line]) - len(lines[error_line].lstrip())
                    lines.insert(error_line + 1, " " * (indent + 4) + "pass\n")
                    fixed = True

            elif "unindent does not match any outer indentation level" in error_msg:
                # Fix indentation issues
                error_line = error_info["line"] - 1 if error_info["line"] else 0
                if error_line < len(lines):
                    # Find proper indentation level
                    for i in range(error_line - 1, -1, -1):
                        if lines[i].strip() and not lines[i].startswith("#"):
                            base_indent = len(lines[i]) - len(lines[i].lstrip())
                            if lines[i].strip().endswith(":"):
                                # This is a block start, use +4
                                correct_indent = base_indent + 4
                            else:
                                # Same level as this line
                                correct_indent = base_indent
                            break
                    else:
                        correct_indent = 0

                    # Fix the indentation
                    if error_line < len(lines) and lines[error_line].strip():
                        lines[error_line] = (
                            " " * correct_indent + lines[error_line].lstrip()
                        )
                        fixed = True

            elif "invalid syntax" in error_msg:
                # Try to fix common invalid syntax patterns
                error_line = error_info["line"] - 1 if error_info["line"] else 0
                if error_line < len(lines):
                    line_content = lines[error_line]

                    # Fix missing colons
                    if line_content.strip().endswith(
                        ")"
                    ) and not line_content.strip().endswith(":"):
                        lines[error_line] = line_content.rstrip() + ":\n"
                        fixed = True

                    # Fix missing parentheses in if statements
                    elif (
                        line_content.strip().startswith("if ")
                        and ":" not in line_content
                    ):
                        lines[error_line] = line_content.rstrip() + ":\n"
                        fixed = True

            # Write back if fixed
            if fixed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"   ❌ Failed to fix {file_path}: {e}")

        return False

    def apply_systematic_fixes(self, syntax_errors):
        """Apply systematic fixes to syntax errors"""
        print("🔧 Applying systematic syntax fixes...")

        # Group errors by type for better handling
        error_groups = {
            "expected_indented_block": [],
            "unindent_mismatch": [],
            "invalid_syntax": [],
            "other": [],
        }

        for error in syntax_errors:
            error_msg = error["error"].lower()
            if "expected an indented block" in error_msg:
                error_groups["expected_indented_block"].append(error)
            elif "unindent" in error_msg:
                error_groups["unindent_mismatch"].append(error)
            elif "invalid syntax" in error_msg:
                error_groups["invalid_syntax"].append(error)
            else:
                error_groups["other"].append(error)

        # Apply fixes by priority
        for error_type, errors in error_groups.items():
            if not errors:
                continue

            print(f"   🔧 Fixing {len(errors)} {error_type} errors...")

            for error in errors:
                file_path = error["file"]
                if os.path.exists(file_path):
                    if self.fix_common_syntax_errors(file_path, error):
                        self.fixes_applied += 1
                        print(f"      ✅ Fixed: {os.path.basename(file_path)}")
                    else:
                        print(
                            f"      ⚠️  Could not auto-fix: {os.path.basename(file_path)}"
                        )

    def validate_fixes(self):
        """Validate that fixes worked"""
        print("✅ Validating fixes...")

        remaining_errors = []
        total_files = 0

        for py_file in self.project_root.rglob("src/**/*.py"):
            total_files += 1
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                remaining_errors.append({"file": str(py_file), "error": str(e)})

        print(f"   📊 Remaining errors: {len(remaining_errors)}")
        print(
            f"   📈 Syntax compliance: {((total_files - len(remaining_errors)) / total_files * 100):.1f}%"
        )

        return remaining_errors

    def run_systematic_fixes(self):
        """Run complete systematic fix process"""
        print("🔧 SYSTEMATIC SYNTAX FIXING")
        print("=" * 40)

        # Create backup
        backup_dir = self.create_emergency_backup()

        # Identify errors
        syntax_errors = self.identify_syntax_errors()

        if not syntax_errors:
            print("✅ No syntax errors found!")
            return True

        # Apply fixes
        self.apply_systematic_fixes(syntax_errors)

        # Validate fixes
        remaining_errors = self.validate_fixes()

        print("\n🎯 SYSTEMATIC FIX SUMMARY")
        print("=" * 30)
        print(f"Initial Errors: {len(syntax_errors)}")
        print(f"Fixes Applied: {self.fixes_applied}")
        print(f"Remaining Errors: {len(remaining_errors)}")
        print(
            f"Success Rate: {((len(syntax_errors) - len(remaining_errors)) / len(syntax_errors) * 100):.1f}%"
        )
        print(f"Backup Location: {backup_dir}")

        if remaining_errors:
            print("\n⚠️  Remaining errors (first 5):")
            for error in remaining_errors[:5]:
                print(f"   {os.path.basename(error['file'])}: {error['error']}")

        return (
            len(remaining_errors) < len(syntax_errors) / 2
        )  # Success if we fixed at least 50%


if __name__ == "__main__":
    fixer = SystematicSyntaxFixer()
    success = fixer.run_systematic_fixes()

    if success:
        print("\n✅ Systematic fixes completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Systematic fixes need manual intervention.")
        sys.exit(1)
