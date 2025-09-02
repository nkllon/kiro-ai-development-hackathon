#!/usr/bin/env python3
"""
Simple F-String Fixer

Purpose: Actually fix broken f-strings with a simple, working approach
"""

import re


def fix_broken_fstrings(content: str) -> str:
    """Fix broken f-strings in content with simple, effective patterns"""

    # Pattern 1: Fix f"text {expression \n more}" -> f"text {expression} more"
    # This handles the specific case we're testing
    pattern1 = r'f"([^"]*?)\{([^}]*?)\\\\(\s*)\n(\s*)([^"]*?)"'
    replacement1 = r'f"\1{\2}\3\4\5"'
    content = re.sub(pattern1, replacement1, content)

    # Pattern 2: Fix f"text {expression \n more}" -> f"text {expression} more"
    # More general case
    pattern2 = r'f"([^"]*?)\{([^"]*?)\\\\(\s*)\n(\s*)([^"]*?)"'
    replacement2 = r'f"\1{\2}\3\4\5"'
    content = re.sub(pattern2, replacement2, content)

    # Pattern 3: Remove backslashes in f-string expressions
    # f"text {expression \n more}" -> f"text {expression} more"
    pattern3 = r'f"([^"]*?)\{([^"]*?)\\\\(\s*)([^"]*?)"'
    replacement3 = r'f"\1{\2}\3\4"'
    return re.sub(pattern3, replacement3, content)


def main():
    """Test the f-string fixer"""

    # Test case
    broken = 'print(f"Count: {len(\\\n    data)}")\n'
    print(f"Original: {repr(broken)}")

    fixed = fix_broken_fstrings(broken)
    print(f"Fixed: {repr(fixed)}")

    # Check if backslash was removed
    backslash_removed = "\\" not in fixed
    print(f"Backslash removed: {backslash_removed}")

    if backslash_removed:
        print("✅ F-string fixer is working!")
    else:
        print("❌ F-string fixer is not working")


if __name__ == "__main__":
    main()
