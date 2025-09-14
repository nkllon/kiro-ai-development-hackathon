from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def unstage_files(self, files: List[str]=None) -> GitOperationResult:
    """Unstage files - placeholder for next task"""
    return self._create_result(success=False, message='unstage_files not yet implemented', error_code='NOT_IMPLEMENTED')

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

