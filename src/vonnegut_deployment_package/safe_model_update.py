#!/usr/bin/env python3
"""
Safe Model Update Script
Demonstrates how to safely manipulate JSON models without corruption
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from model_manager import ModelManager
except ImportError:
    print("❌ Could not import ModelManager - make sure src/model_manager.py exists")
    sys.exit(1)


def main() -> None:
    """Demonstrate safe model manipulation"""
    print("🛡️  Safe Model Manager Demo")
    print("=" * 50)

    # Initialize model manager
    manager = ModelManager()

    # Example 1: Safely update a model field
    print("\n📝 Example 1: Update model field")
    success = manager.update_model_field(
        "project_model_registry",
        ["domains", "python", "linter"],
        "flake8",
    )

    if success:
        print("✅ Model field updated successfully")
    else:
        print("❌ Model field update failed")

    # Example 2: Add a new domain
    print("\n📝 Example 2: Add new domain")
    success = manager.add_model_entry(
        "project_model_registry",
        ["domains"],
        {
            "new_domain": {
                "patterns": ["*.new"],
                "linter": "custom_linter",
                "validator": "custom_validator",
            },
        },
    )

    if success:
        print("✅ New domain added successfully")
    else:
        print("❌ Failed to add new domain")

    # Example 3: List available backups
    print("\n📦 Example 3: List backups")
    backups = manager.list_backups()
    print(f"Found {len(backups)} backups:")
    for backup in backups[:3]:  # Show first 3
        print(f"  - {backup.original_path.name} ({backup.timestamp})")

    # Example 4: Validate model structure
    print("\n🔍 Example 4: Validate model structure")
    schema = {"domains": dict, "requirements_traceability": list}

    is_valid = manager.validate_model_structure("project_model_registry", schema)
    if is_valid:
        print("✅ Model structure is valid")
    else:
        print("❌ Model structure validation failed")

    print("\n🎉 Safe model manipulation complete!")


if __name__ == "__main__":
    main()
