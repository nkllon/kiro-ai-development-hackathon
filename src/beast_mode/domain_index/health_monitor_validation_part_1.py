
def check_domain_health(self, domain_name: str) -> HealthStatus:
    """Check health of a specific domain"""
    with self._time_operation('check_domain_health'):
        self.total_checks += 1
        try:
            if not self.registry_manager:
                raise HealthMonitorError('Registry manager not set')
            domain = self.registry_manager.get_domain(domain_name)
            return self._perform_health_check(domain)
        except Exception as e:
            self.failed_checks += 1
            self._handle_error(e, 'check_domain_health')
            raise HealthCheckFailedError(domain_name, 'full_check', str(e))
