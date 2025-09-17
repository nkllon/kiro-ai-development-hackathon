
def _monitoring_loop(self):
    """Main monitoring loop"""
    while self.running:
        try:
            for service_name, service in self.services.items():
                self._check_service_health(service)
                self._update_service_metrics(service)
            time.sleep(self.config.monitoring.health_check_interval)
        except Exception as e:
            self.logger.error(f'Error in monitoring loop: {e}')
            time.sleep(5)

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

