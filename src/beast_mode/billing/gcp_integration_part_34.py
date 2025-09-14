from src.rm_ddd.core.health import ModuleHealth

class GetconfigurationschemaClass:
    """Auto-generated class for functions."""

    def get_configuration_schema(self) -> Dict[str, Any]:
    """Get configuration schema for the provider"""
    return {'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': True}, 'billing_account_id': {'type': 'string', 'description': 'GCP Billing Account ID'}, 'project_ids': {'type': 'array', 'items': {'type': 'string'}}, 'credentials_path': {'type': 'string', 'description': 'Path to GCP service account credentials'}, 'cache_duration_minutes': {'type': 'integer', 'default': 15, 'minimum': 1}, 'cost_attribution': {'type': 'object', 'properties': {'development': {'type': 'array', 'items': {'type': 'string'}}, 'ai_ml': {'type': 'array', 'items': {'type': 'string'}}, 'networking': {'type': 'array', 'items': {'type': 'string'}}}}, 'budget_alerts': {'type': 'object', 'properties': {'daily_limit_usd': {'type': 'number', 'minimum': 0}, 'hourly_spike_threshold': {'type': 'number', 'minimum': 0}}}}, 'required': ['billing_account_id']}

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

