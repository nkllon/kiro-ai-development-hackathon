
def _select_tools_by_health_and_priority(self, available_tools: List[str]) -> List[str]:
    """
        Select tools based on health status and priority
        """
    if not available_tools:
        return []
    tool_health = {}
    for tool_id in available_tools:
        health_result = self._check_tool_health(tool_id)
        tool_health[tool_id] = health_result['status']
