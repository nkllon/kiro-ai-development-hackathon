
def _get_most_popular_service(self) -> str:
    """Get most popular service across all teams"""
    if not self.service_metrics['service_usage_patterns']:
        return 'pdca_cycle'
    return max(self.service_metrics['service_usage_patterns'].keys(), key=lambda x: self.service_metrics['service_usage_patterns'][x])
