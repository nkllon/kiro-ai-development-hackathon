#!/usr/bin/env python3
"""
Deterministic MDC Editor

This module provides deterministic editing of MDC files using YAML and markdown Python APIs.
Uses ruamel.yaml for YAML frontmatter and markdown-it-py for markdown content.
"""

import re
from pathlib import Path
from typing import Any, Dict, Tuple

try:
    from ruamel.yaml import YAML

    RUAMEL_AVAILABLE = True
except ImportError:
    RUAMEL_AVAILABLE = False

try:
    from markdown_it import MarkdownIt

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class MDCEditor:
    """Deterministic editor for MDC files with YAML frontmatter"""

    def __init__(self):
        self.yaml = YAML() if RUAMEL_AVAILABLE else None
        self.md = MarkdownIt() if MARKDOWN_AVAILABLE else None

        if not RUAMEL_AVAILABLE:
            print("⚠️ Warning: ruamel.yaml not available, using fallback")
        if not MARKDOWN_AVAILABLE:
            print("⚠️ Warning: markdown-it-py not available, using fallback")

    def parse_mdc(self, file_path: str) -> tuple[dict[str, Any], str]:
        """
        Parse MDC file into YAML frontmatter and markdown content

        Args:
            file_path: Path to MDC file

        Returns:
            Tuple of (yaml_data, markdown_content)
        """
        content = Path(file_path).read_text(encoding="utf-8")

        # Split on YAML frontmatter delimiters
        parts = content.split("---", 2)

        if len(parts) < 3:
            # No frontmatter found
            return {}, content

        # Extract YAML frontmatter
        yaml_text = parts[1].strip()
        markdown_content = parts[2].strip()

        # Parse YAML with Cursor format support
        if self.yaml and RUAMEL_AVAILABLE:
            try:
                # Pre-process Cursor-specific MDC format to make it valid YAML
                # Convert "globs: *.py,*.js,*.ts,*.yaml" to "globs:
                # '*.py,*.js,*.ts,*.yaml'"
                processed_text = re.sub(r"globs:\s*([^,\n]+(?:,[^,\n]+)*)", r"globs: '\1'", yaml_text)

                yaml_data = self.yaml.load(processed_text)
                return yaml_data or {}, markdown_content
            except Exception as e:
                print(f"⚠️ Warning: YAML parsing failed: {e}")
                # Fallback to basic parsing
                return self._parse_yaml_fallback(yaml_text), markdown_content
        else:
            # Fallback: basic YAML parsing
            return self._parse_yaml_fallback(yaml_text), markdown_content

    def _parse_yaml_fallback(self, yaml_text: str) -> dict[str, Any]:
        """Fallback YAML parser when ruamel.yaml is not available"""
        yaml_data = {}

        for line in yaml_text.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Handle quoted strings
                if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # Handle lists
                if value.startswith("[") and value.endswith("]"):
                    value = [item.strip().strip("\"'") for item in value[1:-1].split(",")]

                yaml_data[key] = value

        return yaml_data

    def write_mdc(self, file_path: str, yaml_data: dict[str, Any], markdown_content: str):
        """
        Write MDC file with YAML frontmatter and markdown content

        Args:
            file_path: Path to MDC file
            yaml_data: YAML frontmatter data
            markdown_content: Markdown content
        """
        # Generate YAML frontmatter
        if self.yaml and RUAMEL_AVAILABLE:
            from io import StringIO

            stream = StringIO()
            self.yaml.dump(yaml_data, stream)
            yaml_text = stream.getvalue()
        else:
            yaml_text = self._dump_yaml_fallback(yaml_data)

        # Combine into MDC format
        mdc_content = f"---\n{yaml_text}---\n\n{markdown_content}\n"

        # Write file
        Path(file_path).write_text(mdc_content, encoding="utf-8")

    def _dump_yaml_fallback(self, yaml_data: dict[str, Any]) -> str:
        """Fallback YAML dumper when ruamel.yaml is not available"""
        lines = []

        for key, value in yaml_data.items():
            if isinstance(value, list):
                # Handle lists
                items = [f'"{item}"' if " " in str(item) else str(item) for item in value]
                lines.append(f"{key}: [{', '.join(items)}]")
            elif isinstance(value, str) and " " in value:
                # Handle strings with spaces
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def update_yaml_field(self, file_path: str, field: str, value: Any):
        """
        Update a specific YAML field in an MDC file

        Args:
            file_path: Path to MDC file
            field: Field name to update
            value: New value for the field
        """
        yaml_data, markdown_content = self.parse_mdc(file_path)
        yaml_data[field] = value
        self.write_mdc(file_path, yaml_data, markdown_content)

    def add_yaml_field(self, file_path: str, field: str, value: Any):
        """
        Add a new YAML field to an MDC file

        Args:
            file_path: Path to MDC file
            field: Field name to add
            value: Value for the new field
        """
        yaml_data, markdown_content = self.parse_mdc(file_path)
        yaml_data[field] = value
        self.write_mdc(file_path, yaml_data, markdown_content)

    def remove_yaml_field(self, file_path: str, field: str):
        """
        Remove a YAML field from an MDC file

        Args:
            file_path: Path to MDC file
            field: Field name to remove
        """
        yaml_data, markdown_content = self.parse_mdc(file_path)
        if field in yaml_data:
            del yaml_data[field]
            self.write_mdc(file_path, yaml_data, markdown_content)

    def validate_mdc_structure(self, file_path: str) -> bool:
        """
        Validate that an MDC file has proper structure based on model constraints

        Args:
            file_path: Path to MDC file

        Returns:
            True if valid, False otherwise
        """
        try:
            yaml_data, markdown_content = self.parse_mdc(file_path)

            # Check for required fields based on model constraints
            required_fields = ["description", "alwaysApply"]
            missing_fields = [field for field in required_fields if field not in yaml_data]

            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False

            # Check YAML frontmatter format based on model constraints
            always_apply = yaml_data.get("alwaysApply")
            if not isinstance(always_apply, bool):
                print("❌ 'alwaysApply' must be a boolean")
                return False

            # When alwaysApply: true, globs are ignored (optional)
            # When alwaysApply: false, globs are required and respected
            if not always_apply:
                if "globs" not in yaml_data:
                    print("❌ 'globs' field is required when alwaysApply: false")
                    return False

                globs = yaml_data.get("globs")
                if not globs:
                    print("❌ 'globs' field cannot be empty when alwaysApply: false")
                    return False

            # Validate globs format when alwaysApply: false
            if not always_apply:
                globs = yaml_data.get("globs")
                # Support both Cursor format (comma-separated string) and standard
                # format (list)
                if isinstance(globs, str):
                    # Cursor format: "*.py,*.js,*.ts,*.yaml"
                    glob_patterns = [g.strip() for g in globs.split(",")]
                    if not all(glob_patterns):
                        print("❌ 'globs' must contain valid glob patterns")
                        return False
                elif isinstance(globs, list):
                    # Standard format: ["*.py", "*.js", "*.ts", "*.yaml"]
                    if not all(isinstance(g, str) for g in globs):
                        print("❌ 'globs' list must contain strings")
                        return False
                else:
                    print("❌ 'globs' must be a string (Cursor format) or list (standard format)")
                    return False

            print("✅ MDC file structure is valid")
            return True

        except Exception as e:
            print(f"❌ MDC validation failed: {e}")
            return False


def fix_mdc_files():
    """Fix all MDC files in the .cursor/rules directory"""
    editor = MDCEditor()
    rules_dir = Path(".cursor/rules")

    if not rules_dir.exists():
        print("❌ .cursor/rules directory not found")
        return

    mdc_files = list(rules_dir.glob("*.mdc"))
    print(f"🔍 Found {len(mdc_files)} MDC files")

    for mdc_file in mdc_files:
        print(f"\n📝 Processing: {mdc_file.name}")

        try:
            # Validate and fix structure
            if editor.validate_mdc_structure(str(mdc_file)):
                print(f"✅ {mdc_file.name} is already valid")
            else:
                print(f"🔧 Attempting to fix {mdc_file.name}")
                # Try to repair common issues
                yaml_data, markdown_content = editor.parse_mdc(str(mdc_file))

                # Ensure required fields exist based on model constraints
                if "description" not in yaml_data:
                    yaml_data["description"] = f"Rule for {mdc_file.stem}"

                if "globs" not in yaml_data:
                    # Use Cursor format (comma-separated) by default
                    yaml_data["globs"] = "*.py,*.md"

                if "alwaysApply" not in yaml_data:
                    # Default to selective application (respects globs)
                    yaml_data["alwaysApply"] = False

                # Remove triggers field as it's not in our model
                if "triggers" in yaml_data:
                    del yaml_data["triggers"]

                # Write fixed file
                editor.write_mdc(str(mdc_file), yaml_data, markdown_content)
                print(f"✅ Fixed {mdc_file.name}")

        except Exception as e:
            print(f"❌ Failed to process {mdc_file.name}: {e}")


if __name__ == "__main__":
    fix_mdc_files()
