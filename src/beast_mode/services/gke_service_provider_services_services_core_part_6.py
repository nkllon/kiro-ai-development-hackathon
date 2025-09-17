from src.rm_ddd.core.health import ModuleHealth

def request_service(self, service_request: ServiceRequest) -> ServiceResponse:
    """
        Process service request from GKE team
        Implements UC-07, UC-08, UC-09, UC-10 service consumption
        """
    request_start_time = time.time()
    self.logger.info(f'Processing service request: {service_request.request_id} for team {service_request.gke_team_id}')
    try:
        if service_request.service_type not in self.service_registry:
            return self._create_error_response(service_request, 'Service type not available', request_start_time)
        service_info = self.service_registry[service_request.service_type]
        if service_info['current_load'] >= service_info['max_concurrent']:
            return self._create_error_response(service_request, 'Service at capacity, please retry later', request_start_time)
        if service_info['status'] != ServiceStatus.AVAILABLE:
            return self._create_error_response(service_request, f"Service currently {service_info['status'].value}", request_start_time)
        with self.request_lock:
            self.active_requests[service_request.request_id] = service_request
            service_info['current_load'] += 1
        try:
            service_handler = service_info['handler']
            service_result = service_handler(service_request)
            execution_time = time.time() - request_start_time
            response = ServiceResponse(request_id=service_request.request_id, service_type=service_request.service_type, status='success', result=service_result, execution_time_seconds=execution_time, systematic_approach_used=True, velocity_improvement_metrics=self._calculate_velocity_improvements(service_result), timestamp=datetime.now())
            self._update_service_metrics(service_request, response)
            self._update_gke_team_metrics(service_request, response)
            self.logger.info(f'Service request completed successfully: {service_request.request_id}')
            return response
        finally:
            with self.request_lock:
                if service_request.request_id in self.active_requests:
                    del self.active_requests[service_request.request_id]
                service_info['current_load'] -= 1
    except Exception as e:
        self.logger.error(f'Service request failed: {service_request.request_id} - Error: {e}')
        return self._create_error_response(service_request, str(e), request_start_time)

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

