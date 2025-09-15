#!/usr/bin/env python3
"""
Fix RM Syntax Errors - Fix syntax errors from RM interface implementation

This script fixes the syntax errors introduced by the automated RM interface implementation.
"""

import os
import sys
import logging
from pathlib import Path
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)


class RMSyntaxFixer:
    """Fix syntax errors from RM interface implementation"""

    def __init__(self, devpost_path: str = "src/devpost_integration"):
        """Initialize the fixer"""
        self.devpost_path = Path(devpost_path)
        self.files_fixed = 0
        self.errors = []

    def fix_file(self, file_path: Path) -> bool:
        """Fix syntax errors in a single file"""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Check if file has syntax errors
            try:
                compile(content, file_path, "exec")
                logger.info(f"No syntax errors in {file_path.name}")
                return True
            except SyntaxError as e:
                logger.info(f"Fixing syntax errors in {file_path.name}: {e}")

            # Fix common issues
            fixed_content = self._fix_common_issues(content)

            # Write fixed content
            with open(file_path, "w") as f:
                f.write(fixed_content)

            # Verify fix
            try:
                compile(fixed_content, file_path, "exec")
                logger.info(f"Successfully fixed {file_path.name}")
                self.files_fixed += 1
                return True
            except SyntaxError as e:
                logger.error(f"Still has syntax errors after fix: {e}")
                return False

        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            self.errors.append(f"{file_path}: {e}")
            return False

    def _fix_common_issues(self, content: str) -> str:
        """Fix common syntax issues"""
        lines = content.split("\n")
        fixed_lines = []
        in_class = False
        class_indent = 0

        for i, line in enumerate(lines):
            # Detect class definition
            if re.match(r"^class\s+\w+.*:", line):
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                continue

            # Detect end of class (empty line or next class/function at same level)
            if in_class and line.strip() == "":
                # Check if next non-empty line is at class level or higher
                next_line_idx = i + 1
                while next_line_idx < len(lines) and lines[next_line_idx].strip() == "":
                    next_line_idx += 1

                if next_line_idx < len(lines):
                    next_line = lines[next_line_idx]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= class_indent and (
                        next_line.startswith("class ")
                        or next_line.startswith("def ")
                        or next_line.startswith("if __name__")
                    ):
                        in_class = False
                        class_indent = 0
                        fixed_lines.append(line)
                        continue

            # Fix RM interface methods that are outside class
            if (
                line.strip().startswith("def get_module_info")
                or line.strip().startswith("def get_capabilities")
                or line.strip().startswith("def get_dependencies")
                or line.strip().startswith("def check_health")
                or line.strip().startswith("def get_configuration")
                or line.strip().startswith("def update_configuration")
                or line.strip().startswith("def get_metrics")
                or line.strip().startswith("def reset_metrics")
            ):

                if not in_class:
                    # These methods should be inside a class, skip them for now
                    logger.warning(f"Skipping RM method outside class: {line.strip()}")
                    continue

            # Fix indentation issues
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                # This might be a method that should be indented
                if (
                    line.strip().startswith("def ")
                    and i > 0
                    and fixed_lines
                    and fixed_lines[-1].strip()
                    and not fixed_lines[-1].startswith("class ")
                ):
                    # Indent this method
                    line = "    " + line

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_all_files(self) -> Dict[str, Any]:
        """Fix syntax errors in all Python files"""
        logger.info("Starting syntax error fixes")

        python_files = list(self.devpost_path.glob("*.py"))
        results = {
            "total_files": len(python_files),
            "fixed": 0,
            "errors": [],
            "files": {},
        }

        for file_path in python_files:
            if file_path.name == "reflective_module.py":
                continue  # Skip the base module

            logger.info(f"Processing {file_path.name}")
            success = self.fix_file(file_path)

            if success:
                results["fixed"] += 1
                results["files"][file_path.name] = "fixed"
            else:
                results["files"][file_path.name] = "failed"

        results["errors"] = self.errors
        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate fix report"""
        report = f"""
RM Syntax Fix Report
===================

Total Files: {results['total_files']}
Fixed: {results['fixed']}
Errors: {len(results['errors'])}

Success Rate: {(results['fixed'] / results['total_files'] * 100):.1f}%

File Status:
"""

        for file_name, status in results["files"].items():
            report += f"  {file_name}: {status}\n"

        if results["errors"]:
            report += "\nErrors:\n"
            for error in results["errors"]:
                report += f"  {error}\n"

        return report


def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)

    fixer = RMSyntaxFixer()
    results = fixer.fix_all_files()

    # Print report
    print(fixer.generate_report(results))

    # Save report
    with open("rm_syntax_fix_report.txt", "w") as f:
        f.write(fixer.generate_report(results))

    logger.info("RM syntax fix report saved to rm_syntax_fix_report.txt")


if __name__ == "__main__":
    main()
