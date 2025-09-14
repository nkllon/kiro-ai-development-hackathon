#!/usr/bin/env python3
"""
PEP 8 F-String Style Fixer

Purpose: Fix PEP 8 style violations in f-strings, not syntax errors
"""

import ast


def detect_pep8_fstring_violations(content: str) -> list:
    """Detect PEP 8 style violations in f-strings"""

    violations = []

    # Look for backslash-newline patterns across the entire content
    # This handles multi-line f-strings
    if "\\\n" in content:
        # Find the context around the violation
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if 'f"' in line and "\\" in line:
                # This line contains part of a broken f-string
                violations.append(
                    {
                        "line": i,
                        "content": line,
                        "issue": "f-string contains backslash-newline (PEP 8 violation)",
                        "suggestion": "Remove backslash and reformat for readability",
                    }
                )
                break  # Only report the first occurrence

    # Look for very long f-string lines
    lines = content.split("\n")
    for line_num, line in enumerate(lines, 1):
        if 'f"' in line and len(line) > 100:
            violations.append(
                {
                    "line": line_num,
                    "content": line,
                    "issue": "f-string is very long (PEP 8 violation)",
                    "suggestion": "Break into multiple lines or extract variables",
                }
            )

    return violations


def fix_pep8_fstring_style(content: str) -> str:
    """Fix PEP 8 style violations in f-strings"""

    # Use the simple, working approach from our simple fixer
    # Just replace backslash-newline with space, but preserve other newlines

    # Split into lines, process each line
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        if line is None:
            # This line was already merged, skip it
            continue

        if i < len(lines) - 1:  # Not the last line
            next_line = lines[i + 1]

            # If this line ends with backslash, merge with next line
            if line.rstrip().endswith("\\"):
                # Remove the backslash and merge with next line
                fixed_line = line.rstrip()[:-1] + " " + next_line.strip()
                fixed_lines.append(fixed_line)
                # Skip the next line since we've merged it
                lines[i + 1] = None
            else:
                fixed_lines.append(line)
        else:
            # Last line
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def test_pep8_fixer():
    """Test the PEP 8 f-string style fixer"""

    print("🧪 Testing PEP 8 F-String Style Fixer")
    print("=" * 50)

    # Test case with PEP 8 violations
    bad_style_content = """print("Hello")
print(f"Widespread import organization issues: {len( \\\n    import_errors)}")
print("World")"""

    print(f"Original content:\n{bad_style_content}")

    # Detect violations
    violations = detect_pep8_fstring_violations(bad_style_content)
    print(f"\nPEP 8 violations detected: {len(violations)}")

    for violation in violations:
        print(f"  Line {violation['line']}: {violation['issue']}")
        print(f"    Content: {violation['content']}")
        print(f"    Suggestion: {violation['suggestion']}")

    # Fix the style
    fixed_content = fix_pep8_fstring_style(bad_style_content)
    print(f"\nFixed content:\n{fixed_content}")

    # Verify it still parses (should be valid Python)
    try:
        ast.parse(fixed_content)
        print("✅ Fixed content still parses successfully (valid Python)")
    except SyntaxError as e:
        print(f"❌ Fixed content has syntax errors: {e}")

    # Check if PEP 8 violations were fixed
    remaining_violations = detect_pep8_fstring_violations(fixed_content)
    if len(remaining_violations) == 0:
        print("✅ All PEP 8 violations were fixed!")
    else:
        print(f"❌ {len(remaining_violations)} violations remain")


def main():
    """Main entry point"""
    test_pep8_fixer()


if __name__ == "__main__":
    main()
