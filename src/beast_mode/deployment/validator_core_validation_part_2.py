from src.rm_ddd.core.health import ModuleHealth

def _validate_basic_connectivity(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Basic connectivity checks"""
    results = []
    result = self._check_port_connectivity(config.redis.host, config.redis.port, 'Redis port connectivity')
    results.append(result)
    if config.redis.host not in ['localhost', '127.0.0.1']:
        result = self._check_dns_resolution(config.redis.host, 'Redis host DNS resolution')
        results.append(result)
    return results
