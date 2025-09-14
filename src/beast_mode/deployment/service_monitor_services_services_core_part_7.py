from src.rm_ddd.core.health import ModuleHealth

class StartmonitoringClass:
    """Auto-generated class for functions."""

    def start_monitoring(self):
    """Start the monitoring thread"""
    if self.running:
    self.logger.warning('Monitoring is already running')
    return
    self.running = True
    self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
    self.monitoring_thread.start()
    self.logger.info('Service monitoring started')

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

