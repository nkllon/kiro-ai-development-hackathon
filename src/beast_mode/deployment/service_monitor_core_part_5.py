
def stop_service(self, service_name: str, graceful: bool=True) -> bool:
    """Stop a monitored service"""
    if service_name not in self.services:
        self.logger.error(f'Service not found: {service_name}')
        return False
    service = self.services[service_name]
    if service.status != ServiceStatus.RUNNING:
        self.logger.warning(f'Service {service_name} is not running')
        return True
    try:
        service.status = ServiceStatus.STOPPING
        self.logger.info(f'Stopping service: {service_name}')
        if service.process:
            if graceful:
                service.process.terminate()
                try:
                    service.process.wait(timeout=self.config.service_management.get('graceful_shutdown_timeout', 30))
                except subprocess.TimeoutExpired:
                    self.logger.warning(f'Service {service_name} did not stop gracefully, forcing shutdown')
                    service.process.kill()
                    service.process.wait()
            else:
                service.process.kill()
                service.process.wait()
            service.process = None
        service.pid = None
        service.status = ServiceStatus.STOPPED
        self.logger.info(f'Service {service_name} stopped')
        self._trigger_callbacks('service_stopped', service)
        return True
    except Exception as e:
        self.logger.error(f'Failed to stop service {service_name}: {e}')
        return False
