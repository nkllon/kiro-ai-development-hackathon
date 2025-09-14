#!/usr/bin/env python3
"""
CRUD operations for model management system.
Single responsibility: Business CRUD operations (add-item, update-section, etc.).
"""

import json
from src.round_trip_engineering.tools import get_model_registry


class CrudOperations:
    """Handles business CRUD operations."""

    def __init__(self):
        self.registry = get_model_registry()

    def add_item(
        self,
        model_name: str,
        item_id: str,
        description: str,
        title: str = None,
        priority: str = None,
        collection: str = None,
    ) -> tuple[bool, str]:
        """Add an item to a model."""
        try:
            manager = self.registry.get_model(model_name)

            # Let the model manager handle defaults
            kwargs = {}
            if title:
                kwargs["title"] = title
            if priority:
                kwargs["priority"] = priority
            if collection:
                kwargs["collection"] = collection

            success = manager.add_item(item_id, description, **kwargs)
            return True, f"✅ Item added: {success}"

        except Exception as e:
            return False, f"❌ Error adding item: {e}"

    def update_section(self, model_name: str, section: str, updates: str) -> tuple[bool, str]:
        """Update a section in a model."""
        try:
            manager = self.registry.get_model(model_name)
            updates_dict = json.loads(updates)
            success = manager.update_section(section, updates_dict)
            return True, f"✅ Section updated: {success}"

        except Exception as e:
            return False, f"❌ Error updating section: {e}"

    def remove_item(self, model_name: str, item_id: str, collection: str = None) -> tuple[bool, str]:
        """Remove an item from a model."""
        try:
            manager = self.registry.get_model(model_name)
            success = manager.remove_item(item_id, collection or "items")
            return True, f"✅ Item removed: {success}"

        except Exception as e:
            return False, f"❌ Error removing item: {e}"

    def add_section(self, model_name: str, section: str, section_config: str) -> tuple[bool, str]:
        """Add a section to a model."""
        try:
            manager = self.registry.get_model(model_name)
            config_dict = json.loads(section_config)
            success = manager.add_section(section, config_dict)
            return True, f"✅ Section added: {success}"

        except Exception as e:
            return False, f"❌ Error adding section: {e}"

    def remove_section(self, model_name: str, section: str) -> tuple[bool, str]:
        """Remove a section from a model."""
        try:
            manager = self.registry.get_model(model_name)
            success = manager.remove_section(section)
            return True, f"✅ Section removed: {success}"

        except Exception as e:
            return False, f"❌ Error removing section: {e}"

    def create_backup(self, model_name: str) -> tuple[bool, str]:
        """Create a backup of a model."""
        try:
            manager = self.registry.get_model(model_name)
            backup_file = manager.create_backup()
            return True, f"✅ Backup created: {backup_file}"

        except Exception as e:
            return False, f"❌ Error creating backup: {e}"

    def list_backups(self, model_name: str) -> tuple[bool, str]:
        """List available backups for a model."""
        try:
            manager = self.registry.get_model(model_name)
            backups = manager.list_backups()
            output = ["📋 Available backups:"]
            for backup in backups:
                output.append(f"  - {backup}")
            return True, "\n".join(output)

        except Exception as e:
            return False, f"❌ Error listing backups: {e}"

    def restore_backup(self, model_name: str, backup_file: str) -> tuple[bool, str]:
        """Restore a model from backup."""
        try:
            manager = self.registry.get_model(model_name)
            success = manager.restore_backup(backup_file)
            return True, f"✅ Backup restored: {success}"

        except Exception as e:
            return False, f"❌ Error restoring backup: {e}"

    def validate(self, model_name: str) -> tuple[bool, str]:
        """Validate a model."""
        try:
            manager = self.registry.get_model(model_name)
            success = manager.validate()
            return True, f"✅ Model validation: {success}"

        except Exception as e:
            return False, f"❌ Error validating model: {e}"


def create_crud_operations() -> CrudOperations:
    """Factory function to create CRUD operations instance."""
    return CrudOperations()
