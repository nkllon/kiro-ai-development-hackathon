from src.rm_ddd.core.health import ModuleHealth

    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get configuration schema for the provider"""
        return {'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': True}, 'billing_account_id': {'type': 'string', 'description': 'GCP Billing Account ID'}, 'project_ids': {'type': 'array', 'items': {'type': 'string'}}, 'credentials_path': {'type': 'string', 'description': 'Path to GCP service account credentials'}, 'cache_duration_minutes': {'type': 'integer', 'default': 15, 'minimum': 1}, 'cost_attribution': {'type': 'object', 'properties': {'development': {'type': 'array', 'items': {'type': 'string'}}, 'ai_ml': {'type': 'array', 'items': {'type': 'string'}}, 'networking': {'type': 'array', 'items': {'type': 'string'}}}}, 'budget_alerts': {'type': 'object', 'properties': {'daily_limit_usd': {'type': 'number', 'minimum': 0}, 'hourly_spike_threshold': {'type': 'number', 'minimum': 0}}}}, 'required': ['billing_account_id']}

    async def validate_credentials(self) -> bool:
        """Validate GCP credentials"""
        try:
            if self.integration_mode == 'openflow_bridge' and self.billing_client:
                return await self.billing_client.validate_credentials()
            elif self.integration_mode == 'gcp_sdk_direct':
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'Credential validation failed: {e}')
            return False
