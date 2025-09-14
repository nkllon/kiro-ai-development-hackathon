from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status."""
        total_modules = len(self.registered_modules)
        healthy_modules = 0
        unhealthy_modules = 0
        
        for module_id, module_data in self.registered_modules.items():
            health_status = module_data.get('health_status', 'unknown')
            if health_status == 'HEALTHY':
                healthy_modules += 1
            else:
                unhealthy_modules += 1
        
        return {
            'total_registered': total_modules,
            'healthy_modules': healthy_modules,
            'unhealthy_modules': unhealthy_modules,
            'registry_health_percentage': (healthy_modules / total_modules * 100) if total_modules > 0 else 0,
            'last_update': self.last_update
        }

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

    