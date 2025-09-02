#!/usr/bin/env python3
"""
Regenerate all .mdc files using the Python model
"""

import sys
from pathlib import Path

from mdc_generator import MDCGenerator

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main() -> None:
    """Regenerate all .mdc files"""
    generator = MDCGenerator()

    # Find all .mdc files
    mdc_files = list(Path().rglob("*.mdc"))

    if not mdc_files:
        print("No .mdc files found")
        return

    print(f"Found {len(mdc_files)} .mdc files")

    # Regenerate each file
    invalid_files = []
    for mdc_file in mdc_files:
        try:
            print(f"Regenerating {mdc_file}...")
            generator.regenerate_file(mdc_file)
            print(f"✅ Regenerated {mdc_file}")
        except Exception as e:
            print(f"❌ Failed to regenerate {mdc_file}: {e}")
            invalid_files.append(mdc_file)

    if invalid_files:
        print("\nInvalid files:")
        for file in invalid_files:
            print(f"  - {file}")
    else:
        print("\n✅ All .mdc files are valid!")


if __name__ == "__main__":
    main()
