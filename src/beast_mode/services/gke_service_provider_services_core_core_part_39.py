
def _identify_improvement_areas(self, quality_assessment: Dict[str, Any]) -> List[str]:
    """Identify areas needing improvement"""
    areas = []
    if quality_assessment.get('maintainability_index', 0) < 75:
        areas.append('Code maintainability')
    if quality_assessment.get('security_score', 0) < 90:
        areas.append('Security practices')
    if quality_assessment.get('performance_score', 0) < 80:
        areas.append('Performance optimization')
    if quality_assessment.get('gke_compliance_score', 0) < 85:
        areas.append('GKE compliance')
    return areas
