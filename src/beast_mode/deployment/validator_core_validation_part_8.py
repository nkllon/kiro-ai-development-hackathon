from src.rm_ddd.core.health import ModuleHealth

def _validate_security(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Security validation"""
    results = []
    if config.environment.value == 'production':
        if config.redis.password:
            results.append(ValidationResult(name='Redis authentication', passed=True, message='Redis authentication is configured for production'))
        else:
            results.append(ValidationResult(name='Redis authentication', passed=False, message='Redis authentication should be enabled in production'))
        if config.redis.ssl:
            results.append(ValidationResult(name='Redis SSL/TLS', passed=True, message='Redis SSL/TLS is enabled for production'))
        else:
            results.append(ValidationResult(name='Redis SSL/TLS', passed=False, message='Redis SSL/TLS should be enabled in production'))
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

