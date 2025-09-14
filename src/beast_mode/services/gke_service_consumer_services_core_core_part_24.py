
def _calculate_success_rate(self) -> float:
    """Calculate overall service success rate"""
    total = self.service_metrics['total_requests']
    if total == 0:
        return 1.0
    return self.service_metrics['successful_requests'] / total
