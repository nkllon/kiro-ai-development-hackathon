from src.rm_ddd.core.health import ModuleHealth

def _update_service_metrics(self, status: str, execution_time_ms: int):
    """Update service performance metrics"""
    self.service_metrics['total_requests'] += 1
    if status == 'success':
        self.service_metrics['successful_requests'] += 1
    else:
        self.service_metrics['failed_requests'] += 1
    current_avg = self.service_metrics['average_response_time_ms']
    total_requests = self.service_metrics['total_requests']
    new_avg = (current_avg * (total_requests - 1) + execution_time_ms) / total_requests
    self.service_metrics['average_response_time_ms'] = int(new_avg)

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

