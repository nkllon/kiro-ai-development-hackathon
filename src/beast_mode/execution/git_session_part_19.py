from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class CommitchangesClass:
    """Auto-generated class for functions."""

    def commit_changes(self, message: str) -> bool:
    """Commit current changes."""
    try:
    # Add all changes
    subprocess.run(["git", "add", "."], check=True, capture_output=True)

    # Commit changes
    subprocess.run(
    ["git", "commit", "-m", message],
    check=True, capture_output=True
    )

    self.changes_made = True
    self.logger.info(f"Committed changes: {message}")
    return True
    except subprocess.CalledProcessError as e:
    self.logger.error(f"Failed to commit changes: {e}")
    return False

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

