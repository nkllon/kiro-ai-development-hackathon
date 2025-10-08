#!/usr/bin/env python3
"""
🚀 BEAST MODE TARGETED CONVERGENCE
=================================
Direct targeted approach to achieve 95%+ compliance convergence.
"""

import os
import sys
import json
import ast
import re
from datetime import datetime
from pathlib import Path


class BeastModeTargetedConvergence:
    def __init__(self):
        self.project_root = Path.cwd()
        self.target_compliance = 95.0
        self.current_compliance = 0.0
        self.fixes_applied = 0

    def get_current_compliance(self):
        """Get current compliance status"""
        total_files = 0
        valid_files = 0
        error_files = []

        for py_file in self.project_root.rglob("src/**/*.py"):
            total_files += 1
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
                valid_files += 1
            except SyntaxError as e:
                error_files.append(
                    {
                        "file": str(py_file),
                        "error": str(e),
                        "line": e.lineno if hasattr(e, "lineno") else None,
                    }
                )

        compliance = (valid_files / total_files * 100) if total_files > 0 else 0
        return compliance, error_files, total_files

    def apply_beast_mode_syntax_fixes(self):
        """Apply aggressive Beast Mode syntax fixes"""
        print("🚀 BEAST MODE TARGETED SYNTAX FIXES")
        print("=" * 40)

        fixes_applied = 0

        # Get all Python files with syntax errors
        for py_file in self.project_root.rglob("src/**/*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Test if file has syntax errors
                try:
                    ast.parse(content)
                    continue  # File is valid, skip
                except SyntaxError:
                    pass  # File has errors, proceed to fix

                original_content = content

                # Beast Mode Fix 1: Fix missing colons
                content = self.fix_missing_colons(content)

                # Beast Mode Fix 2: Fix indentation issues
                content = self.fix_indentation_issues(content)

                # Beast Mode Fix 3: Fix bracket mismatches
                content = self.fix_bracket_mismatches(content)

                # Beast Mode Fix 4: Fix common syntax patterns
                content = self.fix_common_syntax_patterns(content)

                # Beast Mode Fix 5: Add missing pass statements
                content = self.add_missing_pass_statements(content)

                # Write back if changed
                if content != original_content:
                    try:
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(content)

                        # Verify fix worked
                        ast.parse(content)
                        fixes_applied += 1
                        print(f"   ✅ Fixed: {os.path.basename(py_file)}")

                    except Exception as e:
                        # Revert if fix failed
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(original_content)
                        print(f"   ⚠️  Failed to fix {os.path.basename(py_file)}: {e}")

            except Exception as e:
                print(f"   ❌ Error processing {os.path.basename(py_file)}: {e}")

        return fixes_applied

    def fix_missing_colons(self, content):
        """Fix missing colons in control structures"""
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # Fix missing colons in if/for/while/def/class statements
            if re.match(
                r"^\s*(if|for|while|def|class|try|except|finally|with|async def)\s+",
                line,
            ):
                if not line.rstrip().endswith(":"):
                    # Add colon if missing
                    line = line.rstrip() + ":"

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_indentation_issues(self, content):
        """Fix common indentation issues"""
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # Fix mixed tabs and spaces
            if "\t" in line:
                line = line.expandtabs(4)

            # Fix trailing whitespace
            line = line.rstrip() + "\n" if line.strip() else line

            fixed_lines.append(line)

        return "".join(fixed_lines)

    def fix_bracket_mismatches(self, content):
        """Fix common bracket mismatches"""
        # Fix common patterns
        fixes = [
            (r"\(\s*\)", "()"),  # Empty parentheses with spaces
            (r"\[\s*\]", "[]"),  # Empty brackets with spaces
            (r"\{\s*\}", "{}"),  # Empty braces with spaces
            (r"\(\s*\)", "()"),  # Multiple spaces in parentheses
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)

        return content

    def fix_common_syntax_patterns(self, content):
        """Fix common syntax patterns"""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Fix double colons
            line = re.sub(r"::+", ":", line)

            # Fix missing spaces around operators
            line = re.sub(r"(\w)([=+\-*/])(\w)", r"\1 \2 \3", line)

            # Fix missing spaces after commas
            line = re.sub(r",(\w)", r", \1", line)

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def add_missing_pass_statements(self, content):
        """Add missing pass statements to empty blocks"""
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_lines.append(line)

            # Check if this line ends with colon and next line is empty or has wrong indentation
            if line.strip().endswith(":") and i + 1 < len(lines):
                next_line = lines[i + 1] if i + 1 < len(lines) else ""

                # If next line is empty or has same/lower indentation, add pass
                if not next_line.strip() or len(next_line) - len(
                    next_line.lstrip()
                ) <= len(line) - len(line.lstrip()):
                    indent = len(line) - len(line.lstrip()) + 4
                    fixed_lines.append(" " * indent + "pass")

        return "\n".join(fixed_lines)

    def apply_beast_mode_file_consolidation(self):
        """Apply Beast Mode file consolidation"""
        print("🚀 BEAST MODE FILE CONSOLIDATION")
        print("=" * 40)

        files_consolidated = 0

        # Find and consolidate duplicate files
        file_groups = {}

        for py_file in self.project_root.rglob("src/**/*.py"):
            file_name = py_file.name

            # Group files by base name (without _core_core_core, etc.)
            base_name = re.sub(
                r"(_core_core_core|_services_services_services|_handlers_handlers_handlers|_utils_utils_utils)(\.py)?$",
                "",
                file_name,
            )

            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(py_file)

        # Consolidate groups with multiple files
        for base_name, files in file_groups.items():
            if len(files) > 1:
                # Keep the shortest path (likely the main file)
                main_file = min(files, key=lambda f: len(str(f)))
                duplicate_files = [f for f in files if f != main_file]

                # Delete duplicates
                for dup_file in duplicate_files:
                    try:
                        dup_file.unlink()
                        files_consolidated += 1
                        print(f"   🗑️  Consolidated: {dup_file.name}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to consolidate {dup_file.name}: {e}")

        print(f"   📊 Files consolidated: {files_consolidated}")
        return files_consolidated

    def run_beast_mode_convergence(self):
        """Run Beast Mode targeted convergence"""
        print("🚀 BEAST MODE TARGETED CONVERGENCE")
        print("=" * 50)
        print(f"🎯 Target Compliance: {self.target_compliance}%")
        print()

        # Get initial compliance
        initial_compliance, initial_errors, total_files = self.get_current_compliance()
        self.current_compliance = initial_compliance

        print(f"📊 Initial Compliance: {initial_compliance:.1f}%")
        print(f"📊 Initial Errors: {len(initial_errors)}")
        print(f"📊 Total Files: {total_files}")
        print()

        if initial_compliance >= self.target_compliance:
            print("🎉 TARGET ALREADY ACHIEVED!")
            return True

        # Phase 1: File consolidation
        print("🚀 PHASE 1: FILE CONSOLIDATION")
        files_consolidated = self.apply_beast_mode_file_consolidation()
        print()

        # Phase 2: Syntax fixes
        print("🚀 PHASE 2: SYNTAX FIXES")
        syntax_fixes = self.apply_beast_mode_syntax_fixes()
        print()

        # Get final compliance
        final_compliance, final_errors, final_total_files = (
            self.get_current_compliance()
        )

        # Calculate improvement
        improvement = final_compliance - initial_compliance
        gap_remaining = self.target_compliance - final_compliance

        print("📊 BEAST MODE CONVERGENCE RESULTS")
        print("=" * 40)
        print(f"📈 Initial Compliance: {initial_compliance:.1f}%")
        print(f"📈 Final Compliance: {final_compliance:.1f}%")
        print(f"📈 Improvement: +{improvement:.1f}%")
        print(f"🎯 Gap Remaining: {gap_remaining:.1f}%")
        print(f"🗑️  Files Consolidated: {files_consolidated}")
        print(f"🔧 Syntax Fixes Applied: {syntax_fixes}")
        print(f"📊 Final Errors: {len(final_errors)}")

        # Determine convergence status
        if final_compliance >= self.target_compliance:
            convergence_status = "🎉 CONVERGED"
        elif final_compliance >= self.target_compliance - 2.0:
            convergence_status = "🟡 NEAR_CONVERGENCE"
        elif improvement > 5.0:
            convergence_status = "🟢 SIGNIFICANT_PROGRESS"
        elif improvement > 0.0:
            convergence_status = "🔄 PROGRESS"
        else:
            convergence_status = "❌ NO_PROGRESS"

        print(f"🎯 Convergence Status: {convergence_status}")

        # Save convergence report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "target_compliance": self.target_compliance,
            "initial_compliance": initial_compliance,
            "final_compliance": final_compliance,
            "improvement": improvement,
            "gap_remaining": gap_remaining,
            "files_consolidated": files_consolidated,
            "syntax_fixes_applied": syntax_fixes,
            "convergence_status": convergence_status,
            "total_files": final_total_files,
            "final_errors": len(final_errors),
        }

        os.makedirs(".beast_mode", exist_ok=True)
        with open(".beast_mode/beast_mode_targeted_convergence_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(
            f"💾 Convergence report saved to .beast_mode/beast_mode_targeted_convergence_report.json"
        )

        return final_compliance >= self.target_compliance


if __name__ == "__main__":
    convergence = BeastModeTargetedConvergence()
    success = convergence.run_beast_mode_convergence()

    if success:
        print("\n🎉 BEAST MODE CONVERGENCE ACHIEVED!")
        sys.exit(0)
    else:
        print("\n🔄 BEAST MODE CONVERGENCE IN PROGRESS")
        sys.exit(1)
