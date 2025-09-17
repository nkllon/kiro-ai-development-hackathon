
def _validate_monitoring(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Monitoring validation"""
    results = []
    if config.monitoring.enable_performance_monitoring:
        results.append(ValidationResult(name='Performance monitoring', passed=True, message='Performance monitoring is enabled'))
    if config.monitoring.health_check_interval > 0:
        results.append(ValidationResult(name='Health check configuration', passed=True, message=f'Health checks configured every {config.monitoring.health_check_interval}s'))
    else:
        results.append(ValidationResult(name='Health check configuration', passed=False, message='Health check interval must be positive'))
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

