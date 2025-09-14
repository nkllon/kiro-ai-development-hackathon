#!/usr/bin/env python3
"""
Proper F-String Fixer

Purpose: Fix broken f-strings using proper regex libraries and clear specifications
"""

import ast
import re


class ProperFStringFixer:
    """
    Fix broken f-strings using proper regex patterns and clear specifications
    """

    def __init__(self):
        # Define regex patterns as raw strings to avoid escaping issues
        self.patterns = [
            # Pattern 1: f"text {expression \n more}" -> f"text {expression} more"
            {
                "name": "backslash_newline_in_expression",
                "pattern": r'f"([^"]*?)\{([^}]*?)\\\\(\s*)\n(\s*)([^"]*?)"',
                "replacement": r'f"\1{\2}\3\4\5"',
                "description": "Remove backslash followed by newline in f-string expressions",
            },
            # Pattern 2: f"text {expression \n more}" -> f"text {expression} more"
            {
                "name": "backslash_newline_before_quote",
                "pattern": r'f"([^"]*?)\{([^"]*?)\\\\(\s*)\n(\s*)([^"]*?)"',
                "replacement": r'f"\1{\2}\3\4\5"',
                "description": "Remove backslash followed by newline before closing quote",
            },
            # Pattern 3: f"text {expression \n more}" -> f"text {expression} more"
            {
                "name": "backslash_newline_in_brackets",
                "pattern": r'f"([^"]*?)\{([^}]*?)\\\\(\s*)\n(\s*)([^}]*?)\}',
                "replacement": r'f"\1{\2}\3\4\5}',
                "description": "Remove backslash followed by newline within brackets",
            },
        ]

    def fix_fstrings_in_content(self, content: str) -> str:
        """Fix broken f-strings using the defined patterns"""
        fixed_content = content

        for pattern_info in self.patterns:
            pattern = pattern_info["pattern"]
            replacement = pattern_info["replacement"]
            description = pattern_info["description"]

            # Count matches before replacement
            matches_before = len(re.findall(pattern, fixed_content))

            # Apply the fix
            fixed_content = re.sub(pattern, replacement, fixed_content)

            # Count matches after replacement
            matches_after = len(re.findall(pattern, fixed_content))

            if matches_before > matches_after:
                print(f"✅ Fixed {matches_before - matches_after} instances of: {description}")

        return fixed_content

    def test_patterns(self):
        """Test all patterns with sample data"""
        test_cases = [
            # Test case 1: Basic backslash newline
            {
                "input": 'print(f"Count: {len(\\\n    data)}")\n',
                "expected_fixed": 'print(f"Count: {len(data)}")\n',
                "description": "Basic backslash newline removal",
            },
            # Test case 2: Multiple backslashes
            {
                "input": 'print(f"Sum: {sum(\\\n    values)} and count: {len(\\\n    data)}")\n',
                "expected_fixed": 'print(f"Sum: {sum(values)} and count: {len(data)}")\n',
                "description": "Multiple backslash newline removal",
            },
            # Test case 3: Complex expression
            {
                "input": 'print(f"Result: {complex_function(\\\n    param1, param2)}")\n',
                "expected_fixed": 'print(f"Result: {complex_function(param1, param2)}")\n',
                "description": "Complex function expression",
            },
        ]

        print("🧪 Testing f-string fixer patterns...")

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print(f"Input: {repr(test_case['input'])}")

            fixed = self.fix_fstrings_in_content(test_case["input"])
            print(f"Fixed: {repr(fixed)}")

            # Check if backslash was removed
            backslash_removed = "\\" not in fixed
            print(f"Backslash removed: {backslash_removed}")

            # Check if it matches expected
            matches_expected = fixed == test_case["expected_fixed"]
            print(f"Matches expected: {matches_expected}")

            if backslash_removed and matches_expected:
                print("✅ Test PASSED")
            else:
                print("❌ Test FAILED")

        return True


def main():
    """Test the proper f-string fixer"""

    fixer = ProperFStringFixer()

    # Test the patterns
    fixer.test_patterns()

    # Test with the specific case that was failing
    print("\n🔧 Testing with the specific failing case...")

    broken = 'print(f"Count: {len(\\\n    data)}")\n'
    print(f"Original: {repr(broken)}")

    fixed = fixer.fix_fstrings_in_content(broken)
    print(f"Fixed: {repr(fixed)}")

    # Check if backslash was removed
    backslash_removed = "\\" not in fixed
    print(f"Backslash removed: {backslash_removed}")

    if backslash_removed:
        print("✅ Proper f-string fixer is working!")

        # Verify the fixed content parses
        try:
            ast.parse(fixed)
            print("✅ Fixed content parses successfully!")
        except SyntaxError as e:
            print(f"❌ Fixed content has syntax errors: {e}")
    else:
        print("❌ Proper f-string fixer is not working")


if __name__ == "__main__":
    main()
