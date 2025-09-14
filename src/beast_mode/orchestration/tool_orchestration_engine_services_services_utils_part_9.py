
def _get_tool_health_history(self, tool_id: str) -> List[Dict[str, Any]]:
    """
        Get health history for a tool (simplified implementation)
        """
    current_status = self.tool_health_cache.get(tool_id, ToolStatus.UNKNOWN)
    return [{'timestamp': datetime.now(), 'status': current_status.value, 'tool_id': tool_id}]
