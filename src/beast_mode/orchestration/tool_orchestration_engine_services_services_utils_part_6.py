
def _perform_tool_rca(self, tool_id: str, context: DecisionContext) -> Dict[str, Any]:
    """
        Perform systematic RCA on tool failure
        """
    tool_def = self.tools_registry[tool_id]
    failure_context = {'tool_id': tool_id, 'tool_name': tool_def.name, 'command': tool_def.command, 'dependencies': tool_def.dependencies, 'decision_context': context, 'health_history': self._get_tool_health_history(tool_id)}
    rca_result = self.rca_engine.perform_systematic_rca(failure_context)
    return rca_result
