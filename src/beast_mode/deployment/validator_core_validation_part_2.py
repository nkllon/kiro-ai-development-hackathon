from src.rm_ddd.core.health import ModuleHealth

class ValidatebasicconnectivityClass:
    """Auto-generated class for functions."""

    def _validate_basic_connectivity(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Basic connectivity checks"""
    results = []
    result = self._check_port_connectivity(config.redis.host, config.redis.port, 'Redis port connectivity')
    results.append(result)
    if config.redis.host not in ['localhost', '127.0.0.1']:
    result = self._check_dns_resolution(config.redis.host, 'Redis host DNS resolution')
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

