from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def report_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Provide error reporting and handling"""
        error_report = {
            "error": error,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Validation Error: {error}")
        if context:
            print(f"Context: {context}")
        
        return error_report

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

    