from src.rm_ddd.core.health import ModuleHealth

def remove_service(self, service_name: str):
    """Remove a service from monitoring"""
    if service_name in self.services:
        service = self.services[service_name]
        if service.status == ServiceStatus.RUNNING:
            self.stop_service(service_name)
        del self.services[service_name]
        self.logger.info(f'Removed service from monitor: {service_name}')
