#!/usr/bin/env python3
"""
Debug Regex Capture

Purpose: See what the regex pattern is actually capturing
"""

import re


def debug_regex_capture():
    """Debug what the regex pattern is capturing"""

    # The test line
    test_line = 'print(f"Count: {len(\\\n    data)}")'
    print(f"Test line: {repr(test_line)}")

    # The regex pattern
    pattern = r'f"([^"]*?)\{([^}]*?)\\(\s*)\n(\s*)([^"]*?)"'
    print(f"Pattern: {pattern}")

    # Find all matches
    matches = re.findall(pattern, test_line)
    print(f"Matches found: {len(matches)}")

    for i, match in enumerate(matches):
        print(f"\nMatch {i}:")
        print(f"  Group 1 (before): {repr(match[0])}")
        print(f"  Group 2 (expression): {repr(match[1])}")
        print(f"  Group 3 (ws1): {repr(match[2])}")
        print(f"  Group 4 (ws2): {repr(match[3])}")
        print(f"  Group 5 (after): {repr(match[4])}")

        # Show the full match
        full_match = re.search(pattern, test_line)
        if full_match:
            print(f"  Full match: {repr(full_match.group(0))}")
            print(f"  Match span: {full_match.span()}")

    # Let's try a simpler approach - just find the f-string
    print("\n🧪 Trying simpler approach...")

    # Just find the f-string part
    simple_pattern = r'f"[^"]*"'
    simple_matches = re.findall(simple_pattern, test_line)
    print(f"Simple pattern '{simple_pattern}' found: {simple_matches}")

    # Find where the backslash and newline are
    backslash_pos = test_line.find("\\")
    newline_pos = test_line.find("\n")
    print(f"Backslash position: {backslash_pos}")
    print(f"Newline position: {newline_pos}")

    # Show the context around the backslash
    if backslash_pos != -1:
        start = max(0, backslash_pos - 10)
        end = min(len(test_line), backslash_pos + 10)
        context = test_line[start:end]
        print(f"Context around backslash: {repr(context)}")

    # Show the context around the newline
    if newline_pos != -1:
        start = max(0, newline_pos - 10)
        end = min(len(test_line), newline_pos + 10)
        context = test_line[start:end]
        print(f"Context around newline: {repr(context)}")


if __name__ == "__main__":
    debug_regex_capture()
