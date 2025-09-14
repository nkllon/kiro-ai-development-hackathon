
def _init_gcp_sdk_fallback(self):
    """Initialize using direct GCP SDK (fallback)"""
    self.integration_mode = 'gcp_sdk_direct'
    self.logger.warning('GCP SDK direct integration not yet implemented - using mock data')
    self.billing_client = None
    self.cost_analyzer = None
