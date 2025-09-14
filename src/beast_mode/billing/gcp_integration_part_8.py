from src.rm_ddd.core.health import ModuleHealth

    def _init_gcp_sdk_fallback(self):
        """Initialize using direct GCP SDK (fallback)"""
        self.integration_mode = 'gcp_sdk_direct'
        self.logger.warning('GCP SDK direct integration not yet implemented - using mock data')
        self.billing_client = None
        self.cost_analyzer = None

    async def collect_billing_metrics(self) -> BillingMetrics:
        """
        Collect GCP billing metrics
        
        Uses cached data if available and fresh, otherwise fetches new data
        """
        try:
            if self._is_cache_valid():
                self.logger.debug('Using cached GCP billing metrics')
                return self.cached_metrics
            if self.integration_mode == 'openflow_bridge':
                metrics = await self._collect_via_openflow_bridge()
            else:
                metrics = await self._collect_via_gcp_sdk()
            self.cached_metrics = metrics
            self.last_update = datetime.now()
            self.health_status = HealthStatus(is_healthy=True, status_message='Successfully collected GCP billing metrics', last_check=datetime.now(), metrics={'last_cost': metrics.total_cost_usd})
            return metrics
        except Exception as e:
            self.logger.error(f'Failed to collect GCP billing metrics: {e}')
            self.health_status = HealthStatus(is_healthy=False, status_message=f'Error collecting metrics: {str(e)}', last_check=datetime.now(), metrics={})
            if self.cached_metrics:
                return self.cached_metrics
            else:
                return self._get_mock_metrics()

    async def _collect_via_openflow_bridge(self) -> BillingMetrics:
        """Collect metrics using OpenFlow asset bridge"""
        billing_data = await self.billing_client.get_billing_data()
        analyzed_costs = self.cost_analyzer.analyze_costs(billing_data)
        return BillingMetrics(provider_type=BillingProviderType.GCP, provider_name='Google Cloud Platform', total_cost_usd=analyzed_costs['total_cost'], daily_cost_usd=analyzed_costs['daily_cost'], hourly_burn_rate=analyzed_costs['hourly_burn_rate'], cost_breakdown=analyzed_costs['cost_breakdown'], usage_metrics=analyzed_costs['usage_metrics'], timestamp=datetime.now())

    async def _collect_via_gcp_sdk(self) -> BillingMetrics:
        """Collect metrics using direct GCP SDK integration"""
        return self._get_mock_metrics()

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

