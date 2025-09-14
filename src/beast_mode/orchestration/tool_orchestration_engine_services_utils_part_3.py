from src.rm_ddd.core.health import ModuleHealth

def _execute_tools_systematically(self, selected_tools: List[str], context: DecisionContext, operation_id: str) -> Dict[str, Any]:
    """
        Execute selected tools systematically with health monitoring
        """
    if not selected_tools:
        return {'success': False, 'error': 'No tools selected for execution', 'tools_attempted': [], 'failed_tools': []}
    execution_results = []
    failed_tools = []
    tools_attempted = []
    for tool_id in selected_tools:
        if tool_id not in self.tools_registry:
            self.logger.warning(f'Tool {tool_id} not registered, skipping')
            continue
        tools_attempted.append(tool_id)
        health_result = self._check_tool_health(tool_id)
        if health_result['status'] == ToolStatus.FAILED:
            self.logger.warning(f'Tool {tool_id} is unhealthy, attempting repair')
            repair_result = self._attempt_tool_repair(tool_id)
            if not repair_result['success']:
                failed_tools.append(tool_id)
                continue
        execution_result = self._execute_single_tool(tool_id, context, operation_id)
        execution_results.append(execution_result)
        if execution_result.success:
            return {'success': True, 'primary_result': execution_result, 'fallback_results': execution_results[:-1], 'tools_attempted': tools_attempted, 'failed_tools': failed_tools}
        else:
            failed_tools.append(tool_id)
    return {'success': False, 'primary_result': None, 'fallback_results': execution_results, 'tools_attempted': tools_attempted, 'failed_tools': failed_tools}
