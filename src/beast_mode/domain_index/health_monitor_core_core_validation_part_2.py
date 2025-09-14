
class CheckalldomainsClass:
    """Auto-generated class for functions."""

    def check_all_domains(self) -> HealthStatusCollection:
    """Check health of all domains"""
    with self._time_operation('check_all_domains'):
    try:
    if not self.registry_manager:
    raise HealthMonitorError('Registry manager not set')
    all_domains = self.registry_manager.get_all_domains()
    health_statuses = {}
    if self.parallel_checks and len(all_domains) > 1:
    health_statuses = self._parallel_health_checks(all_domains)
    else:
    for domain_name, domain in all_domains.items():
    try:
    health_statuses[domain_name] = self._perform_health_check(domain)
    except Exception as e:
    self.failed_checks += 1
    self.logger.error(f'Health check failed for {domain_name}: {e}')
    health_statuses[domain_name] = self._create_failed_health_status(str(e))
    self._health_cache.update(health_statuses)
    self._last_full_check = datetime.now()
    self.logger.info(f'Completed health checks for {len(health_statuses)} domains')
    return health_statuses
    except Exception as e:
    self._handle_error(e, 'check_all_domains')
    return {}

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

