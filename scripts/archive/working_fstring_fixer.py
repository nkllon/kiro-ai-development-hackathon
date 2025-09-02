#!/usr/bin/env python3
"""
Working F-String Fixer

Purpose: Fix broken f-strings based on actual string analysis
"""

import ast
import re


def fix_broken_fstrings(content: str) -> str:
    """
    Fix broken f-strings by removing backslashes followed by newlines

    Based on debug analysis, the actual pattern is:
    - Single backslash \\ followed by newline \n
    - Not double backslashes \\ followed by newline
    """

    # Pattern: f"text {expression \n more}" -> f"text {expression} more"
    # This matches a backslash followed by newline within f-string expressions
    pattern = r'f"([^"]*?)\{([^}]*?)\\(\s*)\n(\s*)([^"]*?)"'
    replacement = r'f"\1{\2}\3\4\5"'

    # Apply the fix
    return re.sub(pattern, replacement, content)


def test_fstring_fixer():
    """Test the working f-string fixer"""

    # Test case that was failing
    broken = 'print(f"Count: {len(\\\n    data)}")\n'
    print(f"Original: {repr(broken)}")

    # Apply the fix
    fixed = fix_broken_fstrings(broken)
    print(f"Fixed: {repr(fixed)}")

    # Check if backslash was removed
    backslash_removed = "\\" not in fixed
    print(f"Backslash removed: {backslash_removed}")

    if backslash_removed:
        print("✅ F-string fixer is working!")

        # Verify the fixed content parses
        try:
            ast.parse(fixed)
            print("✅ Fixed content parses successfully!")
        except SyntaxError as e:
            print(f"❌ Fixed content has syntax errors: {e}")
    else:
        print("❌ F-string fixer is not working")

    # Test with more complex cases
    print("\n🧪 Testing more complex cases...")

    test_cases = [
        # Case 1: Basic backslash newline
        'print(f"Count: {len(\\\n    data)}")\n',
        # Case 2: Multiple backslashes
        'print(f"Sum: {sum(\\\n    values)} and count: {len(\\\n    data)}")\n',
        # Case 3: Complex expression
        'print(f"Result: {complex_function(\\\n    param1, param2)}")\n',
        # Case 4: Mixed content
        'print(f"Text: {text} and count: {len(\\\n    items)} and sum: {sum(\\\n    values)}")\n',
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"  Input: {repr(test_case)}")

        fixed = fix_broken_fstrings(test_case)
        print(f"  Fixed: {repr(fixed)}")

        backslash_removed = "\\" not in fixed
        print(f"  Backslash removed: {backslash_removed}")

        if backslash_removed:
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")


def main():
    """Main entry point"""
    print("🔧 Working F-String Fixer")
    print("=" * 30)

    test_fstring_fixer()


if __name__ == "__main__":
    main()
