#!/usr/bin/env python3
"""
AST-Based F-String Fixer

Purpose: Use AST parser to detect and fix broken f-strings
"""

import ast
import re


def find_broken_fstrings(content: str) -> list:
    """Find broken f-strings by trying to parse with AST"""

    broken_fstrings = []

    # Try to parse the content
    try:
        ast.parse(content)
        # If it parses successfully, no broken f-strings
        return []
    except SyntaxError as e:
        # Syntax error found - likely a broken f-string
        error_msg = str(e)

        if "f-string expression part cannot include a backslash" in error_msg:
            # This is exactly what we're looking for!
            broken_fstrings.append(
                {
                    "error": error_msg,
                    "line": getattr(e, "lineno", None),
                    "offset": getattr(e, "offset", None),
                }
            )

    return broken_fstrings


def fix_broken_fstring_line(line: str) -> str:
    """Fix a single line with a broken f-string"""

    # Simple fix: remove backslash followed by newline
    # Pattern: f"text {expression \n more}" -> f"text {expression} more"

    # Find f-strings in the line
    # The issue is that [^}]*? stops at the first } it finds
    # We need to capture the full expression including the closing brace
    fstring_pattern = r'f"([^"]*?)\{([^}]*?)\\(\s*)\n(\s*)([^}]*?)\}'

    def fix_match(match):
        # Extract the parts
        before = match.group(1)  # text before expression
        expression = match.group(2)  # the expression content
        ws1 = match.group(3)  # whitespace after backslash
        ws2 = match.group(4)  # whitespace after newline
        after = match.group(5)  # text after expression

        # Reconstruct without backslash and newline, but keep the expression intact
        # Note: after now includes the closing brace, so we need to add it back
        return f'f"{before}{{{expression}}}{ws1}{ws2}{after}"'

    # Apply the fix
    return re.sub(fstring_pattern, fix_match, line)


def fix_fstrings_in_content(content: str) -> str:
    """Fix broken f-strings in content using AST detection"""

    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines, 1):
        # Check if this line has a broken f-string
        try:
            # Try to parse just this line
            ast.parse(line)
            # Line parses fine, keep it as is
            fixed_lines.append(line)
        except SyntaxError as e:
            # Line has syntax error, try to fix it
            if "f-string expression part cannot include a backslash" in str(e):
                print(f"🔧 Fixing broken f-string on line {i}")
                fixed_line = fix_broken_fstring_line(line)
                fixed_lines.append(fixed_line)
            else:
                # Different syntax error, keep original
                fixed_lines.append(line)

    return "\n".join(fixed_lines)


def test_ast_based_fixer():
    """Test the AST-based f-string fixer"""

    print("🧪 Testing AST-Based F-String Fixer")
    print("=" * 40)

    # Test case that was failing
    broken_content = """print("Hello")
print(f"Count: {len(\\\n    data)}")
print("World")"""

    print(f"Original content:\n{broken_content}")
    print(f"\nContains broken f-string: {find_broken_fstrings(broken_content)}")

    # Fix the content
    fixed_content = fix_fstrings_in_content(broken_content)
    print(f"\nFixed content:\n{fixed_content}")

    # Verify it parses
    try:
        ast.parse(fixed_content)
        print("✅ Fixed content parses successfully!")
    except SyntaxError as e:
        print(f"❌ Fixed content still has syntax errors: {e}")

    # Test individual line fixing
    print("\n🧪 Testing individual line fixing...")

    broken_line = 'print(f"Count: {len(\\\n    data)}")'
    print(f"Broken line: {repr(broken_line)}")

    fixed_line = fix_broken_fstring_line(broken_line)
    print(f"Fixed line: {repr(fixed_line)}")

    # Check if backslash was removed
    backslash_removed = "\\" not in fixed_line
    print(f"Backslash removed: {backslash_removed}")

    if backslash_removed:
        print("✅ Line fixer is working!")

        # Verify the fixed line parses
        try:
            ast.parse(fixed_line)
            print("✅ Fixed line parses successfully!")
        except SyntaxError as e:
            print(f"❌ Fixed line has syntax errors: {e}")
    else:
        print("❌ Line fixer is not working")


def main():
    """Main entry point"""
    test_ast_based_fixer()


if __name__ == "__main__":
    main()
