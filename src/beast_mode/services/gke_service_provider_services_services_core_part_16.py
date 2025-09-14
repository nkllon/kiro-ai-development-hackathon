
def _update_service_metrics(self, request: ServiceRequest, response: ServiceResponse):
    """Update overall service metrics"""
    self.service_metrics['total_requests_served'] += 1
    if response.status == 'success':
        self.service_metrics['successful_requests'] += 1
        velocity_gains = response.velocity_improvement_metrics
        if any((gain > 0 for gain in velocity_gains.values())):
            self.service_metrics['velocity_improvements_delivered'] += 1
    total_time = self.service_metrics['average_response_time'] * (self.service_metrics['total_requests_served'] - 1)
    total_time += response.execution_time_seconds
    self.service_metrics['average_response_time'] = total_time / self.service_metrics['total_requests_served']
    if response.systematic_approach_used:
        systematic_requests = sum((1 for r in self.request_history if r.systematic_approach_used))
        self.service_metrics['systematic_adoption_rate'] = systematic_requests / self.service_metrics['total_requests_served']
    self.request_history.append(response)
    if len(self.request_history) > 1000:
        self.request_history = self.request_history[-1000:]
