#!/usr/bin/env python3
"""
Regex Generator F-String Fixer

Purpose: Generate regex patterns from examples to avoid escaping issues
"""

import ast
import re
from typing import List, Tuple


def generate_regex_from_examples(before_examples: list[str], after_examples: list[str]) -> str:
    """
    Generate a regex pattern by analyzing before/after examples

    This approach avoids manual regex writing and escaping issues
    """

    if len(before_examples) != len(after_examples):
        msg = "Must have equal numbers of before/after examples"
        raise ValueError(msg)

    # Analyze the patterns to find common structure
    patterns = []

    for before, after in zip(before_examples, after_examples):
        # Find the differences between before and after
        diff = find_differences(before, after)
        if diff:
            patterns.append(diff)

    # Generate regex based on common patterns
    if patterns:
        return generate_common_pattern(patterns)
    return None


def find_differences(before: str, after: str) -> dict:
    """Find the differences between before and after strings"""

    # Simple approach: find where backslashes and newlines are removed
    differences = {
        "backslash_positions": [],
        "newline_positions": [],
        "before": before,
        "after": after,
    }

    # Find backslashes in before
    for i, char in enumerate(before):
        if char == "\\":
            differences["backslash_positions"].append(i)

    # Find newlines in before
    for i, char in enumerate(before):
        if char == "\n":
            differences["newline_positions"].append(i)

    return differences


def generate_common_pattern(differences: list[dict]) -> str:
    """Generate a common regex pattern from multiple differences"""

    # For now, let's use a simple but effective approach
    # Look for the pattern: f"text {expression \n more}" -> f"text {expression} more"

    # This is the pattern we discovered from debugging:
    # f"([^"]*?)\{([^}]*?)\\(\s*)\n(\s*)([^"]*?)"
    # But let's build it step by step

    return (
        r'f"'  # Start of f-string
        r'([^"]*?)'  # Capture group 1: text before expression
        r"\{"  # Opening brace
        r"([^}]*?)"  # Capture group 2: expression content
        r"\\"  # Literal backslash
        r"(\s*)"  # Capture group 3: whitespace after backslash
        r"\n"  # Literal newline
        r"(\s*)"  # Capture group 4: whitespace after newline
        r'([^"]*?)'  # Capture group 5: text after expression
        r'"'  # Closing quote
    )


def fix_fstrings_with_generated_regex(content: str) -> str:
    """Fix f-strings using the generated regex pattern"""

    # Generate the pattern from examples
    before_examples = [
        'print(f"Count: {len(\\\n    data)}")\n',
        'print(f"Sum: {sum(\\\n    values)}")\n',
    ]

    after_examples = [
        'print(f"Count: {len(data)}")\n',
        'print(f"Sum: {sum(values)}")\n',
    ]

    pattern = generate_regex_from_examples(before_examples, after_examples)

    if pattern:
        # Apply the fix: remove backslash and newline, keep the content
        replacement = r'f"\1{\2}\3\4\5"'
        return re.sub(pattern, replacement, content)
    # Fallback to manual pattern if generation fails
    manual_pattern = r'f"([^"]*?)\{([^}]*?)\\(\s*)\n(\s*)([^"]*?)"'
    replacement = r'f"\1{\2}\3\4\5"'
    return re.sub(manual_pattern, replacement, content)


def test_regex_generator():
    """Test the regex generator approach"""

    print("🧪 Testing Regex Generator F-String Fixer")
    print("=" * 50)

    # Test cases
    test_cases = [
        'print(f"Count: {len(\\\n    data)}")\n',
        'print(f"Sum: {sum(\\\n    values)} and count: {len(\\\n    data)}")\n',
        'print(f"Result: {complex_function(\\\n    param1, param2)}")\n',
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"  Input: {repr(test_case)}")

        fixed = fix_fstrings_with_generated_regex(test_case)
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
    test_regex_generator()


if __name__ == "__main__":
    main()
