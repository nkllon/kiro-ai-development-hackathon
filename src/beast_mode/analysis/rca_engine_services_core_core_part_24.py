
def _calculate_analysis_confidence(self, analysis_results: Dict[str, Any]) -> float:
    """Calculate confidence score for comprehensive analysis"""
    successful_analyses = sum((1 for result in analysis_results.values() if 'error' not in result))
    total_analyses = len(analysis_results)
    return successful_analyses / max(1, total_analyses)
