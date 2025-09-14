
def is_healthy(self) -> bool:
    """Health assessment for tool orchestrator"""
    tools_healthy = all((status != ToolStatus.FAILED for status in self.tool_status.values()))
    return tools_healthy and (not self._degradation_active)
