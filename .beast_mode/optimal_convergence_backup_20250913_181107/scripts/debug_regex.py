#!/usr/bin/env python3
"""
Debug Regex Patterns

Purpose: Debug why f-string regex patterns aren't matching
"""

import re


def debug_regex_patterns():
    """Debug the regex patterns to see what's happening"""

    # The test case
    test_string = 'print(f"Count: {len(\\\n    data)}")\n'
    print(f"Test string: {repr(test_string)}")
    print(f"Length: {len(test_string)}")
    print(f"Contains backslash: {'\\' in test_string}")
    print(f"Contains newline: {'\\n' in test_string}")

    # Let's look at the string character by character
    print("\nCharacter analysis:")
    for i, char in enumerate(test_string):
        if char == "\\":
            print(f"  {i}: BACKSLASH")
        elif char == "\n":
            print(f"  {i}: NEWLINE")
        elif char == '"':
            print(f"  {i}: QUOTE")
        elif char == "{":
            print(f"  {i}: OPEN_BRACE")
        elif char == "}":
            print(f"  {i}: CLOSE_BRACE")
        else:
            print(f"  {i}: {repr(char)}")

    # Test the pattern step by step
    print("\nTesting pattern step by step:")

    # Pattern: f"([^"]*?)\{([^}]*?)\\\\(\s*)\n(\s*)([^"]*?)"
    pattern = r'f"([^"]*?)\{([^}]*?)\\\\(\s*)\n(\s*)([^"]*?)"'

    print(f"Pattern: {pattern}")

    # Find all matches
    matches = re.findall(pattern, test_string)
    print(f"Matches found: {len(matches)}")
    for i, match in enumerate(matches):
        print(f"  Match {i}: {match}")

    # Let's try a simpler pattern first
    print("\nTrying simpler patterns:")

    # Just find f-strings
    fstring_pattern = r'f"[^"]*"'
    fstring_matches = re.findall(fstring_pattern, test_string)
    print(f"F-string pattern '{fstring_pattern}' found: {fstring_matches}")

    # Find backslashes
    backslash_pattern = r"\\\\"
    backslash_matches = re.findall(backslash_pattern, test_string)
    print(f"Backslash pattern '{backslash_pattern}' found: {len(backslash_matches)}")

    # Find newlines
    newline_pattern = r"\n"
    newline_matches = re.findall(newline_pattern, test_string)
    print(f"Newline pattern '{newline_pattern}' found: {len(newline_matches)}")

    # Let's see what the actual string looks like when we print it
    print(f"\nRaw string representation:")
    print(f"repr(): {repr(test_string)}")
    print(f"str(): {test_string}")

    # Let's try to understand the escaping
    print(f"\nEscaping analysis:")
    print(f"Double backslash count: {test_string.count('\\\\')}")
    print(f"Single backslash count: {test_string.count('\\')}")
    print(f"Newline count: {test_string.count('\\n')}")


if __name__ == "__main__":
    debug_regex_patterns()
