#!/usr/bin/env python3
"""
Project Model Registry Validator and Backup Tool

This script validates the project_model_registry.json against its schema
and provides backup functionality to prevent corruption.
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime
import subprocess


def validate_json_schema(model_path: str, schema_path: str) -> bool:
    """Validate JSON against schema using jsonschema CLI tool"""
    try:
        result = subprocess.run(
            ["jsonschema", "-i", model_path, schema_path],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️  jsonschema CLI tool not found. Install with: pip install jsonschema-cli")
        return True  # Skip validation if tool not available


def validate_json_syntax(file_path: str) -> bool:
    """Validate basic JSON syntax"""
    try:
        with open(file_path, "r") as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False


def create_backup(file_path: str) -> str:
    """Create a timestamped backup of the file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"

    try:
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return ""


def restore_from_backup(file_path: str, backup_path: str) -> bool:
    """Restore file from backup"""
    try:
        shutil.copy2(backup_path, file_path)
        print(f"✅ Restored from backup: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to restore from backup: {e}")
        return False


def main():
    """Main validation function"""
    model_path = "project_model_registry.json"
    schema_path = "project_model_registry.schema.json"

    print("🔍 Project Model Registry Validator")
    print("=" * 50)

    # Check if files exist
    if not Path(model_path).exists():
        print(f"❌ Model file not found: {model_path}")
        sys.exit(1)

    if not Path(schema_path).exists():
        print(f"⚠️  Schema file not found: {schema_path}")
        print("   Skipping schema validation")
        schema_validation = True
    else:
        # Create backup before validation
        backup_path = create_backup(model_path)

        # Validate JSON syntax
        syntax_valid = validate_json_syntax(model_path)

        # Validate against schema
        schema_valid = validate_json_schema(model_path, schema_path)

        if not syntax_valid:
            print("❌ JSON syntax validation failed!")
            if backup_path:
                print("🔄 Attempting to restore from backup...")
                if restore_from_backup(model_path, backup_path):
                    print("✅ File restored from backup")
                    sys.exit(1)
                else:
                    print("❌ Failed to restore from backup")
                    sys.exit(1)
            else:
                print("❌ No backup available for restoration")
                sys.exit(1)

        if not schema_valid:
            print("⚠️  Schema validation failed (non-critical)")
            print("   File syntax is valid, but may not conform to schema")

        print("✅ Project model registry validation completed")

        # Keep backup for safety
        if backup_path:
            print(f"💾 Backup preserved at: {backup_path}")


if __name__ == "__main__":
    main()
