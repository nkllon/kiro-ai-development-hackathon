#!/usr/bin/env python3
"""
Fix Mermaid syntax errors in markdown documents
"""

import re
from pathlib import Path


def fix_mermaid_syntax(file_path: str) -> None:
    """Fix Mermaid syntax errors in markdown file"""

    # Read the file
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Split content into sections
    sections = re.split(r"(```mermaid\s*\n)", content)

    fixed_content = ""
    i = 0

    while i < len(sections):
        if sections[i].startswith("```mermaid"):
            # This is a Mermaid block start
            mermaid_start = sections[i]
            i += 1

            if i < len(sections):
                # This should be the Mermaid content
                mermaid_content = sections[i]
                i += 1

                # Look for the next section that might be a closing marker
                if i < len(sections):
                    next_section = sections[i]

                    # Check if we need to add closing backticks
                    if not next_section.startswith("```"):
                        # Add closing backticks
                        fixed_content += mermaid_start + mermaid_content + "\n```\n"
                    else:
                        # Already has closing backticks
                        fixed_content += mermaid_start + mermaid_content + next_section
                        i += 1
                else:
                    # End of file, add closing backticks
                    fixed_content += mermaid_start + mermaid_content + "\n```\n"
            else:
                # No content after mermaid start
                fixed_content += mermaid_start + "\n```\n"
        else:
            # Regular content
            fixed_content += sections[i]
            i += 1

    # Write the fixed content back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print(f"✅ Fixed Mermaid syntax in {file_path}")


def validate_mermaid_blocks(file_path: str) -> None:
    """Validate Mermaid code blocks for proper syntax"""

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Find all Mermaid blocks
    mermaid_blocks = re.findall(r"```mermaid\s*\n(.*?)(?=\n```|\n---|\n##|\n###|\n$|\n\n)", content, re.DOTALL)

    print(f"Found {len(mermaid_blocks)} Mermaid blocks")

    for i, block in enumerate(mermaid_blocks, 1):
        print(f"\n--- Mermaid Block {i} ---")
        print(block[:200] + "..." if len(block) > 200 else block)

        # Basic validation
        if "graph" in block or "classDiagram" in block or "stateDiagram" in block:
            print("✅ Valid Mermaid diagram type")
        else:
            print("⚠️  Unknown Mermaid diagram type")

        # Check for common syntax issues
        if "-->" in block or "-->" in block:
            print("✅ Contains valid arrows")
        else:
            print("⚠️  No arrows found (might be incomplete)")


if __name__ == "__main__":
    file_path = "docs/GHOSTBUSTERS_COMPREHENSIVE_DESIGN.md"

    if Path(file_path).exists():
        print("🔍 Validating Mermaid blocks...")
        validate_mermaid_blocks(file_path)

        print("\n🔧 Fixing Mermaid syntax...")
        fix_mermaid_syntax(file_path)

        print("\n✅ Mermaid syntax fix complete!")
    else:
        print(f"❌ File not found: {file_path}")
