
def cleanup(self):
    """Cleanup resources and stop all services"""
    self.stop_monitoring()
    for service_name in list(self.services.keys()):
        self.stop_service(service_name)
    self.logger.info('Service monitor cleanup completed')
