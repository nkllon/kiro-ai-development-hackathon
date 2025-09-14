from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class RegisterClass:
    """Auto-generated class for functions."""

    def register(self, name: str, interface_type: InterfaceType,
    file_path: str, line_number: int, methods: List[str]) -> bool:
    """Register an interface"""
    try:
    metadata = InterfaceMetadata(
    name=name,
    type=interface_type,
    status=InterfaceStatus.ACTIVE,
    file_path=file_path,
    line_number=line_number,
    methods=methods,
    created_at=datetime.now(),
    compliance_score=0.0
    )
    self.interfaces[name] = metadata
    self.save_registry()
    return True
    except Exception as e:
    print(f"Error registering interface {name}: {e}")
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

