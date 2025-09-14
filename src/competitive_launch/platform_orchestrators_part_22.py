from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _deploy_core_services(self, resources: GKEResources) -> List[str]:
        """Deploy core Beast Mode services on GKE."""
        services = ['beast-mode-api', 'beast-mode-agents', 'beast-mode-monitoring', 'beast-mode-messaging']
        logger.info(f'Deploying core services: {services}')
        return services

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

