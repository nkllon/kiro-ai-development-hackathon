from src.rm_ddd.core.health import ModuleHealth

def _init_gcp_sdk_fallback(self):
    """Initialize using direct GCP SDK (fallback)"""
    self.integration_mode = 'gcp_sdk_direct'
    self.logger.warning('GCP SDK direct integration not yet implemented - using mock data')
    self.billing_client = None
    self.cost_analyzer = None

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

