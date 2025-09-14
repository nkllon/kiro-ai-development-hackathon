
def restart_service(self, service_name: str) -> bool:
    """Restart a monitored service"""
    if service_name not in self.services:
        self.logger.error(f'Service not found: {service_name}')
        return False
    service = self.services[service_name]
    if service.metrics.restart_count >= service.max_restarts:
        self.logger.error(f'Service {service_name} has exceeded max restarts ({service.max_restarts})')
        service.status = ServiceStatus.FAILED
        return False
    service.status = ServiceStatus.RESTARTING
    self.logger.info(f'Restarting service: {service_name}')
    if not self.stop_service(service_name):
        return False
    time.sleep(service.restart_delay)
    success = self.start_service(service_name)
    if success:
        self._trigger_callbacks('service_restarted', service)
    return success
