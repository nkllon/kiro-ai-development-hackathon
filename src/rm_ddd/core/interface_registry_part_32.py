from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class LoadregistryClass:
    """Auto-generated class for functions."""

    def load_registry(self):
    """Load registry from persistent storage"""
    if os.path.exists(self.registry_file):
    try:
    with open(self.registry_file, 'r') as f:
    data = json.load(f)
    for interface_id, interface_data in data.get('interfaces', {}).items():
    self.interfaces[interface_id] = InterfaceMetadata(**interface_data)
    self.domain_index = data.get('domain_index', {})
    except Exception as e:
    print(f"Warning: Could not load registry: {e}")

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

