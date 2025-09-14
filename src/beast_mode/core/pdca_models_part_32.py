from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class SerializeregistryClass:
    """Auto-generated class for functions."""

    def _serialize_registry(self) -> Dict[str, Any]:
    """Serialize registry for JSON storage"""
    return {
    name: {
    'name': metadata.name,
    'type': metadata.type.value,
    'status': metadata.status.value,
    'file_path': metadata.file_path,
    'line_number': metadata.line_number,
    'methods': metadata.methods,
    'created_at': metadata.created_at.isoformat(),
    'compliance_score': metadata.compliance_score
    }
    for name, metadata in self.interfaces.items()
    }

    # Global registry instance
    registry = InterfaceRegistry()

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

