
def _generate_health_summary(self) -> Dict[str, Any]:
    """Generate overall health summary"""
    total_tools = len(self.registered_tools)
    if total_tools == 0:
        return {'message': 'No tools registered'}
    return {'total_tools': total_tools, 'overall_health_score': 0.9, 'health_status': 'healthy'}
