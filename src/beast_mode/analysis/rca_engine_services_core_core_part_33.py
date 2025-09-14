
def _analyze_infrastructure_details(self, failure: Failure) -> Dict[str, Any]:
    """Analyze infrastructure failure details"""
    return {'error_type': self._get_infrastructure_subcategory(failure), 'system_related': 'system' in failure.error_message.lower(), 'permission_related': 'permission' in failure.error_message.lower(), 'network_related': 'connection' in failure.error_message.lower()}
