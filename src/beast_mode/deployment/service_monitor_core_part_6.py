from src.rm_ddd.core.health import ModuleHealth

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

