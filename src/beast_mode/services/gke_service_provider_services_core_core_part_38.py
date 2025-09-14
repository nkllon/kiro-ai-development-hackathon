
def _calculate_overall_quality_score(self, quality_assessment: Dict[str, Any]) -> float:
    """Calculate overall quality score from assessment"""
    scores = [quality_assessment.get('maintainability_index', 0), quality_assessment.get('security_score', 0), quality_assessment.get('performance_score', 0), quality_assessment.get('gke_compliance_score', 0)]
    return sum(scores) / len(scores)
