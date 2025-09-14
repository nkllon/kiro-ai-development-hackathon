from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class IsreleasetagClass:
    """Auto-generated class for functions."""

    def _is_release_tag(self, tag_name: str) -> bool:
    """Check if tag name indicates a release."""
    release_patterns = ['^v?\\d+\\.\\d+\\.\\d+', '^release', '^r\\d+']
    return any((re.match(pattern, tag_name.lower()) for pattern in release_patterns))

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

