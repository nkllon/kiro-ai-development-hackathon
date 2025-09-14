#!/usr/bin/env python3
"""
MDC Writer - Simple writer for fixed MDC files
"""

from pathlib import Path
from typing import Any, Dict


def write_mdc(file_path: str, yaml_data: dict[str, Any], markdown_content: str):
    """
    Write MDC file with YAML frontmatter and markdown content

    Args:
        file_path: Path to MDC file
        yaml_data: YAML frontmatter data
        markdown_content: Markdown content
    """
    # Generate YAML frontmatter
    yaml_lines = []
    for key, value in yaml_data.items():
        if isinstance(value, bool):
            yaml_lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, str):
            yaml_lines.append(f"{key}: {value}")
        elif isinstance(value, list):
            # Convert list to Cursor format
            items = [str(item) for item in value]
            yaml_lines.append(f"{key}: {','.join(items)}")
        else:
            yaml_lines.append(f"{key}: {value}")

    # Combine into MDC format
    mdc_content = f"---\n{chr(10).join(yaml_lines)}\n---\n\n{markdown_content}\n"

    # Write file
    Path(file_path).write_text(mdc_content, encoding="utf-8")


def main():
    """Test the MDC writer"""
    test_yaml = {"description": "Test rule", "alwaysApply": True, "globs": "*.py,*.js"}
    test_content = "# Test Rule\n\nThis is a test."

    test_file = "test.mdc"
    write_mdc(test_file, test_yaml, test_content)
    print(f"Wrote test file: {test_file}")

    # Clean up
    Path(test_file).unlink()


if __name__ == "__main__":
    main()
