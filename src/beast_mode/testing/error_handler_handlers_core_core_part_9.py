from src.rm_ddd.core.health import ModuleHealth

class MonitorcomponenthealthClass:
    """Auto-generated class for functions."""

    def monitor_component_health(self, component_name: str, operation_result: bool, response_time_ms: float) -> None:
    """
    Monitor health of RCA system components during test execution
    Requirements: 1.4 - Health monitoring for RCA system components
    """
    try:
    current_time = datetime.now()
    if component_name not in self.component_health:
    self._initialize_component_health_entry(component_name)
    health_metrics = self.component_health[component_name]
    health_metrics.last_check_timestamp = current_time
    health_metrics.average_response_time_ms = health_metrics.average_response_time_ms * 0.9 + response_time_ms * 0.1
    if operation_result:
    self._update_success_metrics(health_metrics)
    else:
    self._update_error_metrics(health_metrics, current_time)
    health_metrics.is_healthy = self._assess_component_health(health_metrics)
    if not health_metrics.is_healthy:
    self._consider_degradation(component_name, health_metrics)
    except Exception as e:
    self.logger.error(f'Health monitoring failed for {component_name}: {e}')

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

