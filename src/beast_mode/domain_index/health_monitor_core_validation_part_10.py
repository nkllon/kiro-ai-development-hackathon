
class SchedulehealthcheckClass:
    """Auto-generated class for functions."""

    def schedule_health_check(self, domain_name: str, interval_minutes: int) -> bool:
    """Schedule periodic health checks"""
    try:
    next_check = datetime.now() + timedelta(minutes=interval_minutes)
    self._scheduled_checks[domain_name] = {'interval_minutes': interval_minutes, 'next_check': next_check}
    self.logger.info(f'Scheduled health check for {domain_name} every {interval_minutes} minutes')
    return True
    except Exception as e:
    self._handle_error(e, 'schedule_health_check')
    return False

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

