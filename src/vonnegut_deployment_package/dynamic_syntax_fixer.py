#!/usr/bin/env python3
"""
Dynamic Syntax Fixer
===================

Fixes common syntax patterns in corrupted files dynamically.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Fix syntax errors in template-generated files
"""

import sys
import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DynamicSyntaxFixer:
    """Dynamically fixes common syntax patterns in corrupted files."""

    def __init__(self):
        self.project_root = project_root
        self.fixed_files = []
        self.failed_files = []

    def find_syntax_errors(self) -> List[Path]:
        """Find all files with syntax errors."""
        print("🔍 Scanning for files with syntax errors...")
        error_files = []

        for root, dirs, files in os.walk(self.project_root / "src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                        ast.parse(content)
                    except SyntaxError:
                        error_files.append(file_path)
                        if len(error_files) % 100 == 0:
                            print(
                                f"📁 Found {len(error_files)} files with syntax errors..."
                            )

        print(f"✅ Found {len(error_files)} files with syntax errors")
        return error_files

    def fix_file_dynamically(self, file_path: Path) -> bool:
        """Fix a single file using dynamic pattern matching."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Apply fixes in sequence
            content = self._add_missing_imports(content)
            content = self._fix_indentation_errors(content)
            content = self._fix_class_definitions(content)
            content = self._fix_method_definitions(content)
            content = self._cleanup_malformed_code(content)

            # Validate the fixed content
            ast.parse(content)

            # Write the fixed file
            with open(file_path, "w") as f:
                f.write(content)

            print(f"✅ Fixed {file_path.name}")
            return True

        except Exception as e:
            print(f"❌ Failed to fix {file_path.name}: {e}")
            return False

    def _add_missing_imports(self, content: str) -> str:
        """Add missing imports at the top of the file."""
        lines = content.split("\n")

        # Check if we need to add imports
        needs_reflective_module = (
            "ReflectiveModule" in content
            and "from src.rm_ddd.core.base_reflective_module import ReflectiveModule"
            not in content
        )
        needs_enum = "Enum" in content and "from enum import Enum" not in content
        needs_typing = "Dict[" in content and "from typing import Dict" not in content
        needs_datetime = (
            "datetime" in content and "from datetime import datetime" not in content
        )

        # Find the first non-comment, non-import line
        import_end = 0
        for i, line in enumerate(lines):
            if (
                line.strip()
                and not line.strip().startswith("#")
                and not line.strip().startswith("from ")
                and not line.strip().startswith("import ")
            ):
                import_end = i
                break

        # Insert missing imports
        imports_to_add = []
        if needs_reflective_module:
            imports_to_add.append(
                "from src.rm_ddd.core.base_reflective_module import ReflectiveModule"
            )
        if needs_enum:
            imports_to_add.append("from enum import Enum")
        if needs_typing:
            imports_to_add.append("from typing import Dict, Any")
        if needs_datetime:
            imports_to_add.append("from datetime import datetime")

        if imports_to_add:
            # Insert imports at the beginning
            lines = (
                ["#!/usr/bin/env python3", '"""Auto-generated module"""', ""]
                + imports_to_add
                + [""]
                + lines[import_end:]
            )

        return "\n".join(lines)

    def _fix_indentation_errors(self, content: str) -> str:
        """Fix common indentation errors."""
        lines = content.split("\n")
        fixed_lines = []
        current_indent = 0

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append("")
                continue

            # Handle class definitions
            if stripped.startswith("class ") and ":" in stripped:
                fixed_lines.append("    " * current_indent + stripped)
                current_indent += 1
                continue

            # Handle method definitions
            if stripped.startswith("def ") and ":" in stripped:
                fixed_lines.append("    " * current_indent + stripped)
                continue

            # Handle docstrings
            if stripped.startswith('"""') or stripped.startswith("'''"):
                fixed_lines.append("    " * current_indent + stripped)
                continue

            # Handle return statements and other code
            if (
                stripped.startswith("return")
                or stripped.startswith("if ")
                or stripped.startswith("for ")
                or stripped.startswith("while ")
            ):
                if ":" in stripped:
                    fixed_lines.append("    " * current_indent + stripped)
                    current_indent += 1
                else:
                    fixed_lines.append("    " * current_indent + stripped)
                continue

            # Handle else/elif
            if stripped.startswith("else") or stripped.startswith("elif"):
                current_indent = max(0, current_indent - 1)
                fixed_lines.append("    " * current_indent + stripped)
                if ":" in stripped:
                    current_indent += 1
                continue

            # Handle closing braces and dedentation
            if stripped == "}" or stripped == "]":
                current_indent = max(0, current_indent - 1)
                fixed_lines.append("    " * current_indent + stripped)
                continue

            # Default: maintain current indentation
            fixed_lines.append("    " * current_indent + stripped)

        return "\n".join(fixed_lines)

    def _fix_class_definitions(self, content: str) -> str:
        """Fix malformed class definitions."""
        # Fix class definitions that inherit from both Enum and ReflectiveModule
        content = re.sub(
            r"class\s+(\w+)\(Enum,\s*ReflectiveModule\):",
            r"class \1(ReflectiveModule):",
            content,
        )

        # Fix class definitions missing proper inheritance
        content = re.sub(
            r"class\s+(\w+):(?!\s*$)",  # Class without proper structure
            r"class \1(ReflectiveModule):",
            content,
        )

        return content

    def _fix_method_definitions(self, content: str) -> str:
        """Fix method definitions and add missing implementations."""
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Fix method definitions without proper indentation
            if stripped.startswith("def ") and ":" in stripped:
                # Ensure proper indentation
                if not line.startswith("    "):
                    line = "    " * 4 + stripped

                fixed_lines.append(line)

                # Check if next line needs a pass statement
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if (
                        not next_line
                        or next_line.startswith("def ")
                        or next_line.startswith("class ")
                    ):
                        fixed_lines.append("        pass")
                continue

            # Fix method calls that are missing proper structure
            if stripped.startswith("register_module(") and not stripped.endswith(")"):
                fixed_lines.append("        " + stripped)
                continue

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _cleanup_malformed_code(self, content: str) -> str:
        """Clean up malformed code patterns."""
        lines = content.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            # Remove malformed class definitions
            if stripped.startswith("class ") and "(" not in stripped:
                continue

            # Remove duplicate imports
            if stripped.startswith("from ") and stripped in cleaned_lines:
                continue

            # Remove empty class definitions
            if stripped == "class:" or stripped == "class :":
                continue

            # Fix malformed method calls
            if stripped.startswith("register_module(") and not stripped.endswith(")"):
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def fix_all_files_parallel(self, max_workers: int = 4) -> Dict[str, int]:
        """Fix all files with syntax errors in parallel."""
        print(f"🚀 Starting parallel syntax fixing with {max_workers} workers...")

        error_files = self.find_syntax_errors()

        if not error_files:
            print("✅ No files with syntax errors found!")
            return {"fixed": 0, "failed": 0, "total": 0}

        stats = {"fixed": 0, "failed": 0, "total": len(error_files)}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(self.fix_file_dynamically, file_path): file_path
                for file_path in error_files
            }

            # Process results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        stats["fixed"] += 1
                        self.fixed_files.append(file_path)
                    else:
                        stats["failed"] += 1
                        self.failed_files.append(file_path)
                except Exception as e:
                    print(f"❌ Exception processing {file_path.name}: {e}")
                    stats["failed"] += 1
                    self.failed_files.append(file_path)

                # Progress update
                completed = stats["fixed"] + stats["failed"]
                if completed % 50 == 0:
                    print(
                        f"📊 Progress: {completed}/{stats['total']} files processed..."
                    )

        return stats

    def validate_all_fixed_files(self) -> Dict[str, int]:
        """Validate that all fixed files now have correct syntax."""
        print("🔍 Validating all fixed files...")

        stats = {"valid": 0, "invalid": 0}

        all_files = self.fixed_files + self.failed_files

        for file_path in all_files:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                ast.parse(content)
                stats["valid"] += 1
                if stats["valid"] % 50 == 0:
                    print(f"✅ Validated {stats['valid']} files...")
            except SyntaxError:
                stats["invalid"] += 1
                print(f"❌ Still invalid: {file_path.name}")

        return stats


def main():
    """Main function for dynamic syntax fixer."""
    fixer = DynamicSyntaxFixer()

    print("🚀 Starting Dynamic Syntax Fixer...")

    # Fix all files with syntax errors
    stats = fixer.fix_all_files_parallel(max_workers=4)

    # Validate all fixed files
    validation_stats = fixer.validate_all_fixed_files()

    print(f"\n📊 Final Results:")
    print(f"   Fixed: {stats['fixed']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Valid: {validation_stats['valid']}")
    print(f"   Invalid: {validation_stats['invalid']}")

    return 0 if stats["fixed"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
