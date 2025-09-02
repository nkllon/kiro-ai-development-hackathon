#!/usr/bin/env python3
"""
Fix indentation issues in test files
This script removes merge conflict markers and fixes indentation problems
"""

import os
import re


def fix_test_file(file_path: str) -> None:
    """Fix indentation issues in a test file"""
    print(f"🔧 Fixing {file_path}")

    with open(file_path) as f:
        content = f.read()

    # Remove merge conflict markers
    pattern = r"<<<<<<< HEAD.*?=======.*?>>>>>>> [^\n]+"
    content = re.sub(pattern, "", content, flags=re.DOTALL)

    # Fix common indentation issues
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Skip empty lines
        if not line.strip():
            fixed_lines.append("")
            continue

        # Fix indentation for class definitions
        if line.strip().startswith("class "):
            fixed_lines.append(line.strip())
            continue

        # Fix indentation for method definitions
        if line.strip().startswith("def "):
            fixed_lines.append("    " + line.strip())
            continue

        # Fix indentation for docstrings
        if line.strip().startswith('"""'):
            fixed_lines.append("    " + line.strip())
            continue

        # Fix indentation for assert statements
        if line.strip().startswith("assert "):
            fixed_lines.append("        " + line.strip())
            continue

        # Fix indentation for variable assignments
        if " = " in line and not line.strip().startswith("#"):
            fixed_lines.append("        " + line.strip())
            continue

        # Keep other lines as is
        fixed_lines.append(line)

    # Write the fixed content
    with open(file_path, "w") as f:
        f.write("\n".join(fixed_lines))


def main() -> None:
    """Main function to fix all test files"""
    print("🚀 Fixing test file indentation issues...")

    # Get all test files
    test_files = [
        "tests/test_basic_validation_simple.py",
        "tests/test_cline_fresh_plan_blind_spots.py",
        "tests/test_cline_plan_blind_spots.py",
        "tests/test_code_quality.py",
        "tests/test_code_quality_comprehensive.py",
        "tests/test_core_concepts.py",
        "tests/test_data_fresh_cline_plan.py",
        "tests/test_file_organization.py",
        "tests/test_gemini_2_5_flash_lite_pr_review.py",
        "tests/test_gemini_2_5_preview_pr_review.py",
        "tests/test_healthcare_cdc_requirements.py",
        "tests/test_makefile_integration.py",
        "tests/test_mdc_generator.py",
        "tests/test_rule_compliance.py",
        "tests/test_rule_compliance_enforcement.py",
        "tests/test_security_enhancements.py",
        "tests/test_uv_package_management.py",
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            fix_test_file(file_path)

    print("✅ Test file indentation fixes completed!")


if __name__ == "__main__":
    main()
