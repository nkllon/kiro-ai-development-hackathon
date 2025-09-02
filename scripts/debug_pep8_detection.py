#!/usr/bin/env python3
"""
Debug PEP 8 Detection

Purpose: See why PEP 8 detection isn't working
"""

import re


def debug_pep8_detection():
    """Debug why PEP 8 detection isn't working"""

    print("🔍 Debugging PEP 8 Detection")
    print("=" * 40)

    # Test content
    test_content = """print("Hello")
print(f"Widespread import organization issues: {len( \\\n    import_errors)}")
print("World")"""

    print(f"Test content:\n{test_content}")

    # Check each line
    lines = test_content.split("\n")
    for i, line in enumerate(lines, 1):
        print(f"\nLine {i}: {repr(line)}")
        print(f'  Contains f": {'f"' in line}')
        print(f"  Contains \\\\: {'\\\\' in line}")
        print(f"  Contains \\n: {'\\n' in line}")
        print(f"  Length: {len(line)}")

        # Check for the specific pattern
        if 'f"' in line and "\\\n" in line:
            print("  ✅ PEP 8 violation detected!")
        else:
            print("  ❌ No PEP 8 violation detected")

    # The issue: the content doesn't actually contain '\\\n'
    # It contains ' \\\n' (with a space before the backslash)
    print("\n🔍 The Real Issue:")
    print("The content contains ' \\\\n' (space + backslash + newline)")
    print("Not '\\\\n' (just backslash + newline)")

    # Let's check what's actually in the content
    print("\n🧪 Checking Actual Content:")
    for i, char in enumerate(test_content):
        if char in ["\\", "\n", " "]:
            print(f"  Char {i}: {repr(char)} (ord: {ord(char)})")

    # Now let's fix the detection
    print("\n🧪 Fixed Detection:")
    for i, line in enumerate(lines, 1):
        # Look for space + backslash + newline
        if 'f"' in line and " \\\n" in line:
            print(f"  Line {i}: ✅ PEP 8 violation detected!")
        else:
            print(f"  Line {i}: ❌ No PEP 8 violation")


if __name__ == "__main__":
    debug_pep8_detection()
