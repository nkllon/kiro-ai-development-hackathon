
def _apply_decision_framework(self, candidate_tools: List[Dict[str, Any]], task_requirements: Dict[str, Any], execution_strategy: ExecutionStrategy) -> Dict[str, Any]:
    """Apply decision framework to select optimal tool"""
    if not candidate_tools:
        raise RuntimeError('No candidate tools available')
    if len(candidate_tools) == 1:
        return {'selected_tool': candidate_tools[0], 'confidence': 1.0, 'rationale': 'Only available tool matching requirements', 'systematic_compliance': True}
    tool_scores = []
    for tool in candidate_tools:
        score = self._calculate_tool_score(tool, task_requirements, execution_strategy)
        tool_scores.append((tool, score))
    tool_scores.sort(key=lambda x: x[1]['total_score'], reverse=True)
    selected_tool, best_score = tool_scores[0]
    return {'selected_tool': selected_tool, 'confidence': best_score['confidence'], 'rationale': best_score['rationale'], 'systematic_compliance': best_score['systematic_compliance']}
