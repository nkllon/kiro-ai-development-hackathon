
    def tool_sort_key(tool_id):
        tool_def = self.tools_registry[tool_id]
        health = tool_health[tool_id]
        priority_score = {ToolPriority.CRITICAL: 4, ToolPriority.HIGH: 3, ToolPriority.MEDIUM: 2, ToolPriority.LOW: 1}[tool_def.priority]
        health_score = {ToolStatus.HEALTHY: 3, ToolStatus.DEGRADED: 2, ToolStatus.FAILED: 1, ToolStatus.UNKNOWN: 0}[health]
        return (priority_score, health_score)
    sorted_tools = sorted(available_tools, key=tool_sort_key, reverse=True)
    return sorted_tools[:3]
