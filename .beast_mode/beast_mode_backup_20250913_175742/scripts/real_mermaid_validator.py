#!/usr/bin/env python3
"""Real Mermaid validator that actually works"""

import re
from pathlib import Path


def validate_mermaid_syntax():
    """Actually validate Mermaid syntax properly"""
    file_path = Path("docs/GHOSTBUSTERS_COMPREHENSIVE_DESIGN.md")

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Find all Mermaid blocks with proper regex
    mermaid_pattern = r"```mermaid\s*\n(.*?)\n```"
    mermaid_blocks = re.findall(mermaid_pattern, content, re.DOTALL)

    print(f"🔍 Found {len(mermaid_blocks)} Mermaid blocks")

    # Check for syntax issues
    issues = []

    # Look for double backticks
    double_backtick_pattern = r"```\s*\n```"
    double_backticks = re.findall(double_backtick_pattern, content)
    if double_backticks:
        issues.append(f"❌ Found {len(double_backticks)} instances of double backticks")

    # Look for unclosed Mermaid blocks
    unclosed_pattern = r"```mermaid\s*\n(.*?)(?=\n```|\n---|\n##|\n###|\n$|\n\n)"
    unclosed_blocks = re.findall(unclosed_pattern, content, re.DOTALL)
    if len(unclosed_blocks) != len(mermaid_blocks):
        issues.append(f"❌ Mismatch: {len(unclosed_blocks)} unclosed vs {len(mermaid_blocks)} closed")

    # Look for malformed blocks
    malformed_pattern = r"```mermaid\s*\n.*?\n```\s*\n```"
    malformed_blocks = re.findall(malformed_pattern, content, re.DOTALL)
    if malformed_blocks:
        issues.append(f"❌ Found {len(malformed_blocks)} malformed blocks with extra backticks")

    if issues:
        print("\n🚨 SYNTAX ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")

        # Show the problematic sections
        print("\n🔍 Problematic sections:")
        for i, match in enumerate(re.finditer(r"```mermaid.*?```", content, re.DOTALL)):
            section = content[match.start() : match.end()]
            print(f"\n--- Block {i + 1} ---")
            print(section)
            if "```\n```" in section:
                print("❌ DOUBLE BACKTICKS DETECTED!")
    else:
        print("✅ No syntax issues found!")


if __name__ == "__main__":
    validate_mermaid_syntax()
