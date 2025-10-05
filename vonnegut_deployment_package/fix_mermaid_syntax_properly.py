#!/usr/bin/env python3
"""Actually fix Mermaid syntax properly"""

from pathlib import Path


def fix_mermaid_syntax():
    """Fix the actual Mermaid syntax issues"""
    file_path = Path("docs/GHOSTBUSTERS_COMPREHENSIVE_DESIGN.md")

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the double backticks issue
    # Replace ```\n``` with just ```
    fixed_content = content.replace("```\n```", "```")

    # Write the fixed content back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print("✅ Fixed double backticks issue")

    # Verify the fix
    with open(file_path, encoding="utf-8") as f:
        new_content = f.read()

    if "```\n```" not in new_content:
        print("✅ Double backticks completely eliminated")
    else:
        print("❌ Still have double backticks - fix failed")


if __name__ == "__main__":
    fix_mermaid_syntax()
