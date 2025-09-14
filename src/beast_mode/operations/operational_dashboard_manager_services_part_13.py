from src.rm_ddd.core.health import ModuleHealth

class GetdashboarddataClass:
    """Auto-generated class for functions."""

    def get_dashboard_data(self, dashboard_id: str, include_history: bool=False) -> Dict[str, Any]:
    """
    Get dashboard data
    """
    try:
    if dashboard_id not in self.dashboards:
    return {'error': f'Dashboard {dashboard_id} not found'}
    config = self.dashboards[dashboard_id]
    current_data = self.dashboard_data.get(dashboard_id)
    result = {'dashboard_id': dashboard_id, 'title': config.title, 'type': config.dashboard_type.value, 'enabled': config.enabled, 'current_data': current_data.data if current_data else None, 'last_update': current_data.timestamp if current_data else None}
    if include_history:
    history = self.data_history.get(dashboard_id, [])
    result['history'] = [{'timestamp': entry.timestamp, 'data': entry.data} for entry in history[-50:]]
    return result
    except Exception as e:
    self.logger.error(f'Dashboard data retrieval failed: {str(e)}')
    return {'error': f'Data retrieval failed: {str(e)}'}

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

