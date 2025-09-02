#!/usr/bin/env python3
"""
Simple Direct F-String Fixer

Purpose: Simple approach - just find and remove backslash-newline pairs
"""

import ast


def fix_fstring_backslash_newline(content: str) -> str:
    """
    Simple fix: find '\\\n' and replace with just the newline

    This avoids complex regex and just does the obvious fix
    """

    # Replace backslash followed by newline with just newline
    # This preserves the structure but removes the problematic backslash
    return content.replace("\\\n", "\n")


def test_simple_fixer():
    """Test the simple f-string fixer"""

    print("🧪 Testing Simple Direct F-String Fixer")
    print("=" * 45)

    # Test case that was failing
    broken_content = """print("Hello")
print(f"Count: {len(\\\n    data)}")
print("World")"""

    print(f"Original content:\n{broken_content}")

    # Fix the content
    fixed_content = fix_fstring_backslash_newline(broken_content)
    print(f"\nFixed content:\n{fixed_content}")

    # Check if backslash was removed
    backslash_removed = "\\" not in fixed_content
    print(f"\nBackslash removed: {backslash_removed}")

    if backslash_removed:
        print("✅ Simple fixer is working!")

        # Verify it parses
        try:
            ast.parse(fixed_content)
            print("✅ Fixed content parses successfully!")
        except SyntaxError as e:
            print(f"❌ Fixed content has syntax errors: {e}")
    else:
        print("❌ Simple fixer is not working")

    # Test with more cases
    print("\n🧪 Testing more cases...")

    test_cases = [
        'print(f"Count: {len(\\\n    data)}")\n',
        'print(f"Sum: {sum(\\\n    values)} and count: {len(\\\n    data)}")\n',
        'print(f"Result: {complex_function(\\\n    param1, param2)}")\n',
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"  Input: {repr(test_case)}")

        fixed = fix_fstring_backslash_newline(test_case)
        print(f"  Fixed: {repr(fixed)}")

        backslash_removed = "\\" not in fixed
        print(f"  Backslash removed: {backslash_removed}")

        if backslash_removed:
            print("  ✅ PASSED")

            # Verify it parses
            try:
                ast.parse(fixed)
                print("  ✅ Parses successfully")
            except SyntaxError as e:
                print(f"  ❌ Parse error: {e}")
        else:
            print("  ❌ FAILED")


def main():
    """Main entry point"""
    test_simple_fixer()


if __name__ == "__main__":
    main()
