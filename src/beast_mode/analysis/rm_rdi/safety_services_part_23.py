from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _validate_initial_safety(self) -> bool:
        """Validate initial safety conditions"""
        if os.getuid() == 0:
            self.logger.error('SAFETY VIOLATION: Running as root user')
            return False
        if self.limits.max_cpu_percent > 50:
            self.logger.warning('CPU limit >50% may impact system performance')
        return True

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

