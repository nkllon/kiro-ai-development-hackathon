
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
