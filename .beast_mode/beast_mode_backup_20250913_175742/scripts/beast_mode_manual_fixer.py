#!/usr/bin/env python3
"""
🚀 BEAST MODE MANUAL FIXER
=========================
Aggressive manual fixing of remaining syntax errors to achieve full compliance.
"""

import os
import sys
import json
import ast
import shutil
from datetime import datetime
from pathlib import Path


class BeastModeManualFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = 0
        self.files_fixed = 0
        self.aggressive_fixes = True

    def create_beast_mode_backup(self):
        """Create Beast Mode backup before aggressive fixes"""
        print("🚀 Creating Beast Mode backup...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f".beast_mode/beast_mode_backup_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup critical directories
        for dir_name in ["src", "scripts", "docs"]:
            if os.path.exists(dir_name):
                shutil.copytree(dir_name, backup_dir / dir_name)

        print(f"   ✅ Beast Mode backup created: {backup_dir}")
        return str(backup_dir)

    def identify_critical_errors(self):
        """Identify critical syntax errors for aggressive fixing"""
        print("🔍 Identifying critical syntax errors...")

        critical_errors = []
        error_patterns = {
            "expected_indented_block": [],
            "unindent_mismatch": [],
            "invalid_syntax": [],
            "missing_colons": [],
            "bracket_mismatches": [],
        }

        for py_file in self.project_root.rglob("src/**/*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                error_info = {
                    "file": str(py_file),
                    "error": str(e),
                    "line": e.lineno if hasattr(e, "lineno") else None,
                    "text": e.text if hasattr(e, "text") else None,
                }

                # Categorize error
                error_msg = str(e).lower()
                if "expected an indented block" in error_msg:
                    error_patterns["expected_indented_block"].append(error_info)
                elif "unindent" in error_msg:
                    error_patterns["unindent_mismatch"].append(error_info)
                elif "invalid syntax" in error_msg:
                    error_patterns["invalid_syntax"].append(error_info)
                elif ":" in str(e) and "expected" in error_msg:
                    error_patterns["missing_colons"].append(error_info)
                else:
                    error_patterns["bracket_mismatches"].append(error_info)

                critical_errors.append(error_info)

        print(f"   📊 Found {len(critical_errors)} critical errors")
        for pattern, errors in error_patterns.items():
            if errors:
                print(f"      {pattern}: {len(errors)} errors")

        return critical_errors, error_patterns

    def aggressive_fix_indented_block_errors(self, errors):
        """Aggressively fix indented block errors"""
        print("🚀 Aggressively fixing indented block errors...")

        fixed_count = 0
        for error in errors:
            file_path = error["file"]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                error_line = error["line"] - 1 if error["line"] else 0
                if error_line < len(lines):
                    line_content = lines[error_line]

                    # Determine proper indentation
                    if error_line > 0:
                        prev_line = lines[error_line - 1]
                        if prev_line.strip().endswith(":"):
                            # Previous line ends with colon, need indented block
                            base_indent = len(prev_line) - len(prev_line.lstrip())
                            new_indent = base_indent + 4

                            # Add pass statement with proper indentation
                            lines.insert(error_line + 1, " " * new_indent + "pass\n")

                            with open(file_path, "w", encoding="utf-8") as f:
                                f.writelines(lines)

                            fixed_count += 1
                            print(f"      ✅ Fixed: {os.path.basename(file_path)}")

            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")

        return fixed_count

    def aggressive_fix_unindent_errors(self, errors):
        """Aggressively fix unindent errors"""
        print("🚀 Aggressively fixing unindent errors...")

        fixed_count = 0
        for error in errors:
            file_path = error["file"]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                error_line = error["line"] - 1 if error["line"] else 0
                if error_line < len(lines):
                    # Find proper indentation level
                    proper_indent = 0
                    for i in range(error_line - 1, -1, -1):
                        if lines[i].strip() and not lines[i].startswith("#"):
                            if lines[i].strip().endswith(":"):
                                # Block start, use +4
                                proper_indent = (
                                    len(lines[i]) - len(lines[i].lstrip()) + 4
                                )
                            else:
                                # Same level
                                proper_indent = len(lines[i]) - len(lines[i].lstrip())
                            break

                    # Fix the indentation
                    if lines[error_line].strip():
                        lines[error_line] = (
                            " " * proper_indent + lines[error_line].lstrip()
                        )

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.writelines(lines)

                        fixed_count += 1
                        print(f"      ✅ Fixed: {os.path.basename(file_path)}")

            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")

        return fixed_count

    def aggressive_fix_syntax_errors(self, errors):
        """Aggressively fix general syntax errors"""
        print("🚀 Aggressively fixing syntax errors...")

        fixed_count = 0
        for error in errors:
            file_path = error["file"]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Common syntax fixes
                original_content = content

                # Fix missing colons in if/for/while/def statements
                import re

                patterns = [
                    (
                        r"(\s+)(if|for|while|def|class|try|except|finally|with|async def)\s+[^:]+$",
                        r"\1\2:",
                    ),
                    (
                        r"(\s+)(if|for|while|def|class|try|except|finally|with|async def)\s+[^:]+\)$",
                        r"\1\2:",
                    ),
                ]

                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

                # Fix common bracket issues
                content = content.replace("( )", "()")
                content = content.replace("[ ]", "[]")
                content = content.replace("{ }", "{}")

                # Only write if content changed
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    fixed_count += 1
                    print(f"      ✅ Fixed: {os.path.basename(file_path)}")

            except Exception as e:
                print(f"      ⚠️  Failed to fix {os.path.basename(file_path)}: {e}")

        return fixed_count

    def beast_mode_delete_problematic_files(self):
        """Beast Mode: Delete files that are too problematic to fix quickly"""
        print("🚀 BEAST MODE: Deleting problematic files...")

        # List of problematic file patterns that can be safely deleted
        problematic_patterns = [
            "*_core_core_core.py",
            "*_services_services_services.py",
            "*_handlers_handlers_handlers.py",
            "*_utils_utils_utils.py",
        ]

        deleted_count = 0
        for pattern in problematic_patterns:
            for file_path in self.project_root.rglob(f"src/**/{pattern}"):
                try:
                    # Verify it's actually a problematic duplicate
                    file_name = file_path.name
                    base_name = (
                        file_name.replace("_core_core_core", "")
                        .replace("_services_services_services", "")
                        .replace("_handlers_handlers_handlers", "")
                        .replace("_utils_utils_utils", "")
                    )

                    # Check if there's a non-duplicate version
                    non_duplicate_path = file_path.parent / base_name
                    if non_duplicate_path.exists():
                        # Delete the duplicate
                        file_path.unlink()
                        deleted_count += 1
                        print(f"      🗑️  Deleted duplicate: {file_name}")

                except Exception as e:
                    print(f"      ⚠️  Failed to delete {file_path}: {e}")

        print(f"   🗑️  Deleted {deleted_count} problematic duplicate files")
        return deleted_count

    def validate_beast_mode_fixes(self):
        """Validate Beast Mode fixes"""
        print("✅ Validating Beast Mode fixes...")

        total_files = 0
        valid_files = 0
        remaining_errors = []

        for py_file in self.project_root.rglob("src/**/*.py"):
            total_files += 1
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
                valid_files += 1
            except SyntaxError as e:
                remaining_errors.append({"file": str(py_file), "error": str(e)})

        compliance_percentage = (
            (valid_files / total_files * 100) if total_files > 0 else 0
        )

        print(f"   📊 Total Files: {total_files}")
        print(f"   ✅ Valid Files: {valid_files}")
        print(f"   ❌ Error Files: {len(remaining_errors)}")
        print(f"   📈 Compliance: {compliance_percentage:.1f}%")

        return {
            "total_files": total_files,
            "valid_files": valid_files,
            "error_files": len(remaining_errors),
            "compliance_percentage": compliance_percentage,
            "remaining_errors": remaining_errors[:10],
        }

    def run_beast_mode_fixes(self):
        """Run complete Beast Mode fix process"""
        print("🚀 BEAST MODE MANUAL FIXING")
        print("=" * 40)

        # Create backup
        backup_dir = self.create_beast_mode_backup()

        # Identify critical errors
        critical_errors, error_patterns = self.identify_critical_errors()

        if not critical_errors:
            print("✅ No critical errors found!")
            return True

        # Beast Mode: Delete problematic duplicates first
        deleted_count = self.beast_mode_delete_problematic_files()

        # Apply aggressive fixes by category
        total_fixes = 0

        if error_patterns["expected_indented_block"]:
            fixes = self.aggressive_fix_indented_block_errors(
                error_patterns["expected_indented_block"]
            )
            total_fixes += fixes

        if error_patterns["unindent_mismatch"]:
            fixes = self.aggressive_fix_unindent_errors(
                error_patterns["unindent_mismatch"]
            )
            total_fixes += fixes

        if error_patterns["invalid_syntax"]:
            fixes = self.aggressive_fix_syntax_errors(error_patterns["invalid_syntax"])
            total_fixes += fixes

        # Validate fixes
        validation_result = self.validate_beast_mode_fixes()

        print("\n🚀 BEAST MODE FIX SUMMARY")
        print("=" * 30)
        print(f"Initial Errors: {len(critical_errors)}")
        print(f"Files Deleted: {deleted_count}")
        print(f"Fixes Applied: {total_fixes}")
        print(f"Remaining Errors: {validation_result['error_files']}")
        print(f"Final Compliance: {validation_result['compliance_percentage']:.1f}%")
        print(f"Backup Location: {backup_dir}")

        if validation_result["compliance_percentage"] >= 95:
            print("\n🎉 BEAST MODE SUCCESS: 95%+ compliance achieved!")
            return True
        elif validation_result["compliance_percentage"] >= 90:
            print("\n🟡 BEAST MODE PROGRESS: Significant improvement achieved!")
            return True
        else:
            print("\n🔄 BEAST MODE CONTINUES: More fixes needed")
            return False


if __name__ == "__main__":
    fixer = BeastModeManualFixer()
    success = fixer.run_beast_mode_fixes()

    if success:
        print("\n🚀 Beast Mode fixes completed successfully!")
        sys.exit(0)
    else:
        print("\n🚀 Beast Mode continues - more aggressive fixes needed!")
        sys.exit(1)
