#!/usr/bin/env python3
"""
MDC Parser - Direct parsing of Cursor MDC files without YAML kludges
"""

import re
from pathlib import Path
from typing import Any, Dict, Tuple


class MDCParser:
    """Direct MDC file parser that understands Cursor's format"""

    def __init__(self):
        self.delimiter_pattern = re.compile(r"^---$", re.MULTILINE)

    def parse_mdc(self, file_path: str) -> tuple[dict[str, Any], str]:
        """
        Parse MDC file directly without YAML complications

        Args:
            file_path: Path to MDC file

        Returns:
            Tuple of (yaml_data, markdown_content)
        """
        content = Path(file_path).read_text(encoding="utf-8")

        # Find delimiters
        lines = content.split("\n")
        delimiter_positions = []

        for i, line in enumerate(lines):
            if line.strip() == "---":
                delimiter_positions.append(i)

        if len(delimiter_positions) != 2:
            msg = f"MDC file must have exactly 2 '---' delimiters, found {len(delimiter_positions)}"
            raise ValueError(msg)

        # Extract frontmatter
        frontmatter_start = delimiter_positions[0]
        frontmatter_end = delimiter_positions[1]
        frontmatter_lines = lines[frontmatter_start + 1 : frontmatter_end]

        # Parse frontmatter directly
        yaml_data = self._parse_frontmatter(frontmatter_lines)

        # Extract markdown content
        markdown_content = "\n".join(lines[frontmatter_end + 1 :])

        return yaml_data, markdown_content

    def _parse_frontmatter(self, lines: list[str]) -> dict[str, Any]:
        """Parse frontmatter lines directly without YAML"""
        yaml_data = {}

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Handle different value types
                if value.lower() == "true":
                    yaml_data[key] = True
                elif value.lower() == "false":
                    yaml_data[key] = False
                elif value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                    yaml_data[key] = value[1:-1]
                elif value.startswith("[") and value.endswith("]"):
                    # Handle YAML list format
                    items = [item.strip().strip("\"'") for item in value[1:-1].split(",")]
                    yaml_data[key] = items
                else:
                    # Assume string value
                    yaml_data[key] = value

        return yaml_data

    def validate_mdc_structure(self, file_path: str) -> bool:
        """
        Validate MDC file structure using direct parsing

        Args:
            file_path: Path to MDC file

        Returns:
            True if valid, False otherwise
        """
        try:
            yaml_data, markdown_content = self.parse_mdc(file_path)

            # Check required fields
            required_fields = ["description", "alwaysApply"]
            missing_fields = [field for field in required_fields if field not in yaml_data]

            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False

            # Validate alwaysApply is boolean
            always_apply = yaml_data.get("alwaysApply")
            if not isinstance(always_apply, bool):
                print("❌ 'alwaysApply' must be a boolean")
                return False

            # When alwaysApply: false, globs are required
            if not always_apply:
                if "globs" not in yaml_data:
                    print("❌ 'globs' field is required when alwaysApply: false")
                    return False

                globs = yaml_data.get("globs")
                if not globs:
                    print("❌ 'globs' field cannot be empty when alwaysApply: false")
                    return False

                # Validate globs format
                if isinstance(globs, str):
                    # Cursor format: "*.py,*.js,*.ts,*.yaml"
                    glob_patterns = [g.strip() for g in globs.split(",")]
                    if not all(glob_patterns):
                        print("❌ 'globs' must contain valid glob patterns")
                        return False
                elif isinstance(globs, list):
                    # Standard format: ["*.py", "*.js", "*.ts", ".yaml"]
                    if not all(isinstance(g, str) for g in globs):
                        print("❌ 'globs' list must contain strings")
                        return False
                else:
                    print("❌ 'globs' must be a string (Cursor format) or list (standard format)")
                    return False

            # Check markdown content
            if not markdown_content.strip():
                print("❌ No markdown content found")
                return False

            # Heuristic fuzzy checks for rule purpose vs configuration
            self._validate_rule_heuristics(file_path, yaml_data, markdown_content)

            print("✅ MDC file structure is valid")
            return True

        except Exception as e:
            print(f"❌ MDC validation failed: {e}")
            return False

    def _validate_rule_heuristics(self, file_path: str, yaml_data: dict[str, Any], markdown_content: str):
        """
        Heuristic fuzzy checks for rule purpose vs configuration

        Args:
            file_path: Path to MDC file
            yaml_data: Parsed YAML frontmatter
            markdown_content: Markdown content
        """
        filename = Path(file_path).stem.lower()
        description = yaml_data.get("description", "").lower()
        always_apply = yaml_data.get("alwaysApply")
        globs = yaml_data.get("globs", "")

        # Check for mismatched rule purpose and configuration
        warnings = []

        # YAML-specific rules should target YAML files
        if any(keyword in filename or keyword in description for keyword in ["yaml", "yml", "config", "template"]):
            if always_apply is True:
                warnings.append("YAML-specific rule with alwaysApply: true - consider targeting YAML files specifically")
            elif always_apply is False and globs:
                # Check if globs include YAML extensions
                yaml_extensions = [
                    ".yaml",
                    ".yml",
                    ".yaml.j2",
                    ".yml.j2",
                    ".yaml.template",
                    ".yml.template",
                ]
                glob_patterns = globs.split(",") if isinstance(globs, str) else globs
                has_yaml_targets = any(any(ext in pattern for ext in yaml_extensions) for pattern in glob_patterns)
                if not has_yaml_targets:
                    warnings.append("YAML rule doesn't target YAML file extensions")

        # Security rules should be universal
        if any(keyword in filename or keyword in description for keyword in ["security", "credential", "auth", "encrypt"]):
            if always_apply is False:
                warnings.append("Security rule with alwaysApply: false - consider making it universal")

        # Language-specific rules should target appropriate files
        if any(keyword in filename or keyword in description for keyword in ["python", "py", "js", "typescript", "ts"]):
            if always_apply is True:
                warnings.append("Language-specific rule with alwaysApply: true - consider targeting specific file types")

        # Print warnings
        for warning in warnings:
            print(f"⚠️  Heuristic warning: {warning}")


def main():
    """Test the MDC parser"""
    parser = MDCParser()

    # Test with a known good file
    test_file = ".cursor/rules/security.mdc"
    if Path(test_file).exists():
        print(f"Testing {test_file}:")
        try:
            yaml_data, content = parser.parse_mdc(test_file)
            print(f"YAML data: {yaml_data}")
            print(f"Content length: {len(content)}")
            print(f"Validation: {parser.validate_mdc_structure(test_file)}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
