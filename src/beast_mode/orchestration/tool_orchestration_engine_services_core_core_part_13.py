
def _generate_orchestration_recommendations(self, execution_result: Dict[str, Any], decision_result: Dict[str, Any], confidence_result: Dict[str, Any]) -> List[str]:
    """
        Generate recommendations based on orchestration results
        """
    recommendations = []
    if execution_result['success']:
        recommendations.append('Tool orchestration completed successfully')
        if confidence_result['confidence_level'] == DecisionConfidenceLevel.LOW:
            recommendations.append('Consider improving domain intelligence to increase decision confidence')
    else:
        recommendations.append('Tool orchestration failed - systematic repair attempted')
        failed_tools = execution_result.get('failed_tools', [])
        if failed_tools:
            recommendations.append(f"Consider alternative tools for: {', '.join(failed_tools)}")
        if confidence_result['confidence_level'] == DecisionConfidenceLevel.HIGH:
            recommendations.append('High confidence decision failed - review domain intelligence accuracy')
    total_time = execution_result.get('total_execution_time_ms', 0)
    if total_time > 5000:
        recommendations.append('Execution time exceeded 5 seconds - consider tool optimization')
    decision_method = decision_result.get('decision_method', '')
    if decision_method == 'full_multi_stakeholder_analysis':
        recommendations.append('Low confidence required full analysis - consider expanding domain intelligence')
    return recommendations
