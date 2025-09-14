from src.rm_ddd.core.health import ModuleHealth

def _update_service_metrics(self, service: MonitoredService):
    """Update metrics for a service"""
    if service.status != ServiceStatus.RUNNING or not service.pid:
        return
    try:
        process = psutil.Process(service.pid)
        service.metrics.cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        service.metrics.memory_mb = memory_info.rss / 1024 / 1024
        service.metrics.memory_percent = process.memory_percent()
        try:
            service.metrics.open_files = len(process.open_files())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        try:
            service.metrics.connections = len(process.connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        if service.started_at:
            service.metrics.uptime_seconds = time.time() - service.started_at
    except psutil.NoSuchProcess:
        service.status = ServiceStatus.FAILED
        service.pid = None
    except Exception as e:
        self.logger.error(f'Error updating metrics for {service.name}: {e}')

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

