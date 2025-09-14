
def add_service(self, service: MonitoredService):
    """Add a service to monitor"""
    self.services[service.name] = service
    self.logger.info(f'Added service to monitor: {service.name}')
