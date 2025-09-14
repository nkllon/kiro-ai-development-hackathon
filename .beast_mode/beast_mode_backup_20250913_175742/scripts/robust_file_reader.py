#!/usr/bin/env python3
"""
Robust File Reader
Handles multiple encodings with fallback strategy
"""

import logging
from pathlib import Path
from typing import Any, Optional


class RobustFileReader:
    """Reads files with multiple encoding support"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        # Common encodings to try
        self.encodings = [
            "utf-8",
            "big5",  # Traditional Chinese
            "gbk",  # Simplified Chinese
            "latin-1",  # Western European
            "cp1252",  # Windows-1252
            "iso-8859-1",  # ISO Latin-1
            "shift_jis",  # Japanese
            "euc-jp",  # Japanese
            "euc-kr",  # Korean
        ]
        self.failed_files: dict[str, list[str]] = {}

    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file with multiple encoding attempts"""
        if not file_path.exists():
            return None

        # Try each encoding
        for encoding in self.encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.warning(f"Error reading {file_path}: {e}")
                continue

        # If all encodings fail, log and return None
        self.logger.warning(f"Could not read {file_path} with any encoding")
        self.failed_files[str(file_path)] = self.encodings.copy()
        return None

    def can_read_file(self, file_path: Path) -> bool:
        """Check if file can be read with any encoding"""
        return self.read_file(file_path) is not None

    def get_failed_files_report(self) -> dict[str, Any]:
        """Get report of files that couldn't be read"""
        return {
            "total_failed": len(self.failed_files),
            "failed_files": self.failed_files,
            "suggested_encodings": self._suggest_new_encodings(),
        }

    def _suggest_new_encodings(self) -> list[str]:
        """Suggest new encodings based on failures"""
        # If we have many failures, suggest adding more encodings
        if len(self.failed_files) > 5:
            return ["utf-16", "utf-32", "ascii", "mac_roman", "cp437"]
        return []


def main() -> None:
    """Test the robust file reader"""
    reader = RobustFileReader()

    # Test with the problematic file
    test_file = Path(
        ".venv/lib/python3.12/site-packages/joblib/test/test_func_inspect_special_encoding.py",
    )

    if test_file.exists():
        content = reader.read_file(test_file)
        if content:
            print("✅ Successfully read file with encoding detection!")
            print(f"First 100 chars: {content[:100]}")
        else:
            print("❌ Could not read file with any encoding")

    # Test with a normal file
    normal_file = Path("scripts/robust_file_reader.py")
    content = reader.read_file(normal_file)
    if content:
        print("✅ Successfully read normal file")

    # Show failed files report
    report = reader.get_failed_files_report()
    if report["total_failed"] > 0:
        print(f"\n📊 Failed files: {report['total_failed']}")
        for file, encodings in report["failed_files"].items():
            print(f"   {file}: tried {encodings}")


if __name__ == "__main__":
    main()
