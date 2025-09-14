from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class GetinterfacerighttouseClass:
    """Auto-generated class for functions."""

    def get_interface_right_to_use(self, interface_name: str, interface_type: InterfaceType,
    creator: str, purpose: str) -> tuple[bool, Optional[InterfaceMetadata], str]:
    """Check right-to-use before creating an interface"""
    existing = self.find_interface_by_name_and_type(interface_name, interface_type)
    if existing:
    # Check if creator is the same
    if existing.created_by != creator:
    return False, existing, f"Interface '{interface_name}' already exists and is owned by {existing.created_by}"

    # Check if interface is deprecated
    if existing.status == InterfaceStatus.DEPRECATED:
    return True, existing, f"Interface '{interface_name}' is deprecated and can be replaced"

    # Check if purpose is different
    if purpose.lower() not in existing.description.lower():
    return False, existing, f"Interface '{interface_name}' already serves this purpose"

    return False, existing, f"Interface '{interface_name}' already exists with similar functionality"

    return True, None, "Interface creation allowed"

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

