from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def can_process(self, input_data: bytes, filename: Optional[str] = None) -> bool:
        """
        Default implementation checks if format is in supported list.
        Subclasses should override for more sophisticated checking.
        """
        try:
            router = FormatRouter()
            detected_format = router.detect_format(input_data, filename)
            return detected_format.lower() in self._supported_formats
        except ValueError:
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

    