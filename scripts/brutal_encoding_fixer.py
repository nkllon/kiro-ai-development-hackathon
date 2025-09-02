#!/usr/bin/env python3
"""
Brutal Encoding Fixer
Fixes encoding issues with extreme prejudice - assumes UTF-8 and forces it
"""

import logging
from pathlib import Path
from typing import Optional


class BrutalEncodingFixer:
    """Fixes encoding issues by forcing UTF-8 with extreme prejudice"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.fixed_files: list[str] = []
        self.failed_files: list[str] = []

    def read_file_brutally(self, file_path: Path) -> Optional[str]:
        """Read file with extreme prejudice - force UTF-8"""
        if not file_path.exists():
            return None

        try:
            # Try UTF-8 first
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                # Force UTF-8 with error handling
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                    # Decode with errors='replace' - replace bad bytes with
                    return raw_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                self.logger.error(f"Brutal encoding failed for {file_path}: {e}")
                self.failed_files.append(str(file_path))
                return None

    def fix_encoding_brutally(self, file_path: Path) -> bool:
        """Fix file encoding by forcing UTF-8"""
        if not file_path.exists():
            return False

        try:
            # Read with brutal method
            content = self.read_file_brutally(file_path)
            if content is None:
                return False

            # Write back as UTF-8
            file_path.write_text(content, encoding="utf-8")
            self.fixed_files.append(str(file_path))
            return True

        except Exception as e:
            self.logger.error(f"Failed to fix {file_path}: {e}")
            self.failed_files.append(str(file_path))
            return False

    def fix_directory_brutally(self, directory: Path) -> None:
        """Fix all Python files in directory with extreme prejudice"""
        print(f"🔨 Fixing encoding in {directory} with extreme prejudice...")

        for py_file in directory.rglob("*.py"):
            if self.fix_encoding_brutally(py_file):
                print(f"✅ Fixed: {py_file}")
            else:
                print(f"❌ Failed: {py_file}")

    def get_report(self) -> dict:
        """Get brutal fixing report"""
        return {
            "fixed_files": len(self.fixed_files),
            "failed_files": len(self.failed_files),
            "fixed_list": self.fixed_files,
            "failed_list": self.failed_files,
        }


def main() -> None:
    """Main function - fix encoding with extreme prejudice"""
    print("🔨 BRUTAL ENCODING FIXER")
    print("=" * 40)
    print("⚠️  WARNING: This will force UTF-8 encoding!")
    print("⚠️  Security implications: May corrupt non-UTF-8 files!")
    print("=" * 40)

    fixer = BrutalEncodingFixer()

    # Fix the problematic file
    problem_file = Path(".venv/lib/python3.12/site-packages/joblib/test/test_func_inspect_special_encoding.py")

    if problem_file.exists():
        print(f"🔨 Fixing problematic file: {problem_file}")
        if fixer.fix_encoding_brutally(problem_file):
            print("✅ BRUTAL FIX SUCCESSFUL!")
        else:
            print("❌ BRUTAL FIX FAILED!")

    # Test reading after fix
    if problem_file.exists():
        content = fixer.read_file_brutally(problem_file)
        if content:
            print("✅ File now readable with brutal method!")
            print(f"First 100 chars: {content[:100]}")
        else:
            print("❌ Still can't read file!")

    # Show report
    report = fixer.get_report()
    print("\n📊 BRUTAL FIXING REPORT:")
    print(f"   Files fixed: {report['fixed_files']}")
    print(f"   Files failed: {report['failed_files']}")


if __name__ == "__main__":
    main()
