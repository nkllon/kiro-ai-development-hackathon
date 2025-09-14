
def force_tool_health_refresh(self) -> Dict[str, Any]:
    """
        Force refresh of all tool health statuses
        """
    refresh_results = {}
    for tool_id in self.tools_registry.keys():
        health_result = self._check_tool_health(tool_id)
        refresh_results[tool_id] = health_result['status'].value
    return {'refreshed_tools': len(refresh_results), 'health_status': refresh_results, 'timestamp': datetime.now()}
