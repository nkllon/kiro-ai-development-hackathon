from src.rm_ddd.core.health import ModuleHealth

def _create_error_response(self, request: ServiceRequest, error_message: str, start_time: float) -> ServiceResponse:
    """Create error response for failed service requests"""
    return ServiceResponse(request_id=request.request_id, service_type=request.service_type, status='failure', result={'error': error_message}, execution_time_seconds=time.time() - start_time, systematic_approach_used=False, velocity_improvement_metrics={}, timestamp=datetime.now(), error_message=error_message)

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

