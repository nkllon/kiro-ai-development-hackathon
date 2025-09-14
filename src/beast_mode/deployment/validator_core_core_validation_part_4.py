from src.rm_ddd.core.health import ModuleHealth

class ValidateservicehealthClass:
    """Auto-generated class for functions."""

    def _validate_service_health(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Service health validation"""
    results = []
    expected_processes = ['redis-server', 'python']
    for process_name in expected_processes:
    result = self._check_process_running(process_name)
    results.append(result)
    log_files = [config.agent.mailbox_log_file]
    for log_file in log_files:
    result = self._check_log_file_health(log_file)
    results.append(result)
    return results

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

