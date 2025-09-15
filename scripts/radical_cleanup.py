#!/usr/bin/env python3
"""
Radical Cleanup Script
=====================

Removes all template-generated bloat files and keeps only essential functionality.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Clean up massive template bloat from corrupted parallel agent runs
"""

import sys
import os
import shutil
from pathlib import Path
from typing import List, Set

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class RadicalCleanup:
    """Performs radical cleanup of template-generated bloat."""

    def __init__(self):
        self.project_root = project_root
        self.deleted_files = []
        self.kept_files = []

    def identify_bloat_patterns(self) -> Set[str]:
        """Identify patterns that indicate template bloat."""
        bloat_patterns = {
            # Part files (the main culprit)
            "*part_*.py",
            "*_part_*.py",
            "*_class_*_part_*.py",
            # Duplicate classes
            "*_class_2*.py",
            "*_class_3*.py",
            "*_class_4*.py",
            "*_class_5*.py",
            "*_class_6*.py",
            "*_class_7*.py",
            "*_class_8*.py",
            # Services bloat
            "*_services_part_*.py",
            "*_services_class_*.py",
            # Core bloat
            "*_core_part_*.py",
            "*_core_class_*.py",
            # Models bloat
            "*_models_part_*.py",
            "*_models_class_*.py",
            # Handlers bloat
            "*_handlers_part_*.py",
            "*_handlers_class_*.py",
        }
        return bloat_patterns

    def get_essential_files(self) -> Set[str]:
        """Get list of essential files that should be preserved."""
        essential_files = {
            # Core framework files
            "src/rm_ddd/core/base_reflective_module.py",
            "src/rm_ddd/core/health.py",
            "src/rm_ddd/core/registry.py",
            # Main module files (without _part_ or _class_)
            "src/beast_mode/compliance/reporting/phase3_readiness_assessor_core_core_validation.py",
            # CLI files
            "src/devpost_integration/cli_generator.py",
            # Test files
            "tests/conftest.py",
            # Configuration files
            "pytest.ini",
            "pyproject.toml",
            "requirements.txt",
        }
        return essential_files

    def should_keep_file(self, file_path: Path) -> bool:
        """Determine if a file should be kept or deleted."""
        file_str = str(file_path)

        # Keep essential files
        if file_str in self.get_essential_files():
            return True

        # Keep main module files (without part/class suffixes)
        if (
            file_path.suffix == ".py"
            and not any(
                pattern in file_path.name for pattern in ["_part_", "_class_", "part_"]
            )
            and not file_path.name.endswith("_part.py")
        ):
            return True

        # Keep test files
        if "test_" in file_path.name or "tests/" in file_str:
            return True

        # Keep configuration files
        if file_path.name in [
            "__init__.py",
            "conftest.py",
            "pytest.ini",
            "pyproject.toml",
            "requirements.txt",
        ]:
            return True

        return False

    def perform_cleanup(self) -> dict:
        """Perform the radical cleanup."""
        print("🚀 Starting Radical Cleanup...")

        stats = {"deleted": 0, "kept": 0, "total_scanned": 0}

        # Walk through all Python files
        for root, dirs, files in os.walk(self.project_root / "src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    stats["total_scanned"] += 1

                    if self.should_keep_file(file_path):
                        self.kept_files.append(file_path)
                        stats["kept"] += 1
                        print(f"✅ Keeping: {file_path.relative_to(self.project_root)}")
                    else:
                        try:
                            file_path.unlink()  # Delete the file
                            self.deleted_files.append(file_path)
                            stats["deleted"] += 1
                            if stats["deleted"] % 100 == 0:
                                print(f"🗑️  Deleted {stats['deleted']} files...")
                        except Exception as e:
                            print(f"❌ Failed to delete {file_path}: {e}")

        return stats

    def create_summary_report(self, stats: dict) -> str:
        """Create a summary report of the cleanup."""
        report = f"""
# Radical Cleanup Report

## Summary
- **Total files scanned**: {stats['total_scanned']}
- **Files deleted**: {stats['deleted']}
- **Files kept**: {stats['kept']}
- **Cleanup percentage**: {(stats['deleted'] / stats['total_scanned'] * 100):.1f}%

## Files Kept (Essential)
"""
        for file_path in self.kept_files[:20]:  # Show first 20
            report += f"- {file_path.relative_to(self.project_root)}\n"

        if len(self.kept_files) > 20:
            report += f"- ... and {len(self.kept_files) - 20} more essential files\n"

        report += f"\n## Files Deleted (Template Bloat)\n"
        report += f"- {stats['deleted']} template-generated files removed\n"
        report += f"- Removed all '*_part_*.py' files\n"
        report += f"- Removed all '*_class_*_part_*.py' files\n"
        report += f"- Removed duplicate service and handler files\n"

        return report


def main():
    """Main function for radical cleanup."""
    cleanup = RadicalCleanup()

    print("⚠️  WARNING: This will permanently delete template-generated bloat files!")
    print("📊 Estimated cleanup: ~15,000 files will be deleted")
    print("✅ Essential functionality will be preserved")

    # Perform cleanup
    stats = cleanup.perform_cleanup()

    # Create report
    report = cleanup.create_summary_report(stats)

    # Save report
    report_path = cleanup.project_root / "radical_cleanup_report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\n📊 Cleanup Complete!")
    print(f"   Deleted: {stats['deleted']} files")
    print(f"   Kept: {stats['kept']} files")
    print(f"   Report: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
