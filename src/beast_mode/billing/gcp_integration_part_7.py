from src.rm_ddd.core.health import ModuleHealth

    def _init_openflow_bridge(self):
        """Initialize using OpenFlow asset bridge"""
        try:
            self.billing_client = GCPBillingClientBridge(self.config)
            self.cost_analyzer = CostAnalyzerBridge(self.config)
            self.integration_mode = 'openflow_bridge'
        except Exception as e:
            self.logger.error(f'Failed to initialize OpenFlow bridge: {e}')
            self._init_gcp_sdk_fallback()

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

