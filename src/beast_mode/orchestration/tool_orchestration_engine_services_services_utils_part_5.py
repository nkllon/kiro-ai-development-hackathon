
def _handle_tool_failures_systematically(self, failed_tools: List[str], context: DecisionContext, operation_id: str) -> Dict[str, Any]:
    """
        Handle tool failures using systematic RCA and repair
        """
    if not failed_tools:
        return {'repairs_successful': False, 'repaired_tools': []}
    repaired_tools = []
    repair_results = []
    for tool_id in failed_tools:
        self.logger.info(f'Attempting systematic repair of tool: {tool_id}')
        rca_result = self._perform_tool_rca(tool_id, context)
        repair_result = self._attempt_systematic_repair(tool_id, rca_result)
        repair_results.append(repair_result)
        if repair_result['success']:
            repaired_tools.append(tool_id)
            self.orchestration_metrics['tools_repaired'] += 1
    return {'repairs_successful': len(repaired_tools) > 0, 'repaired_tools': repaired_tools, 'repair_results': repair_results}
