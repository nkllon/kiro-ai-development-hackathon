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
