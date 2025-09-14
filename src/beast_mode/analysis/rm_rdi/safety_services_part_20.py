from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class GetsafetystatusClass:
    """Auto-generated class for functions."""

    def get_safety_status(self) -> SafetyStatus:
    """Get current safety status"""
    violations = self.resource_monitor.check_limits()
    usage = self.resource_monitor.get_current_usage()
    return SafetyStatus(is_safe=len(violations) == 0 and (not self.emergency_shutdown_triggered), resource_usage=usage, violations=violations, last_check=datetime.now(), kill_switch_armed=self.kill_switch.is_armed)

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

