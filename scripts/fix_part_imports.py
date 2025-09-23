#!/usr/bin/env python3
"""
Fix Part Imports Script
======================

Automatically fix files that import from deleted part_ files.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Clean up remaining part_ imports after radical cleanup
"""

import os
import re
from pathlib import Path


def fix_part_imports(file_path: str) -> bool:
    """Fix part imports in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file has part imports
        if "from ." in content and "part_" in content:
            print(f"Fixing part imports in: {file_path}")

            # Remove all lines that import from part_ files
            lines = content.split("\n")
            filtered_lines = []

            for line in lines:
                if "part_" in line and ("from ." in line or "import" in line):
                    print(f"  Removing: {line.strip()}")
                    continue
                filtered_lines.append(line)

            # Write back the cleaned content
            cleaned_content = "\n".join(filtered_lines)

            # If the file is now empty or only has whitespace, create a minimal valid module
            if not cleaned_content.strip():
                module_name = Path(file_path).stem
                cleaned_content = f'''#!/usr/bin/env python3
"""
{module_name.replace('_', ' ').title()}
{'=' * len(module_name)}

Auto-generated module after cleanup.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Minimal valid module
"""

from typing import Dict, Any
from datetime import datetime


class {module_name.title().replace('_', '')}:
    """Minimal valid class."""
    
    def __init__(self):
        self.module_id = "{module_name}"
        self.timestamp = datetime.now()
    
    def get_info(self) -> Dict[str, Any]:
        """Get module info."""
        return {{
            'module_id': self.module_id,
            'timestamp': self.timestamp.isoformat()
        }}
'''

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)

            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main function."""
    src_dir = Path("src")

    if not src_dir.exists():
        print("src directory not found")
        return

    fixed_count = 0
    total_count = 0

    # Find all Python files
    for py_file in src_dir.rglob("*.py"):
        total_count += 1

        if fix_part_imports(str(py_file)):
            fixed_count += 1

    print(f"\nSummary:")
    print(f"Total files processed: {total_count}")
    print(f"Files fixed: {fixed_count}")
    print(f"Files unchanged: {total_count - fixed_count}")


if __name__ == "__main__":
    main()
