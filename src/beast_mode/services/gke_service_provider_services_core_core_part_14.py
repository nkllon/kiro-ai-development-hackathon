
def _create_error_response(self, request: ServiceRequest, error_message: str, start_time: float) -> ServiceResponse:
    """Create error response for failed service requests"""
    return ServiceResponse(request_id=request.request_id, service_type=request.service_type, status='failure', result={'error': error_message}, execution_time_seconds=time.time() - start_time, systematic_approach_used=False, velocity_improvement_metrics={}, timestamp=datetime.now(), error_message=error_message)
