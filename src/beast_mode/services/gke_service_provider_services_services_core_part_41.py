from src.rm_ddd.core.health import ModuleHealth

def _identify_compliance_gaps(self, quality_assessment: Dict[str, Any]) -> List[str]:
    """Identify compliance gaps"""
    gaps = []
    if quality_assessment.get('security_score', 0) < 90:
        gaps.append('Security compliance below 90%')
    if quality_assessment.get('gke_compliance_score', 0) < 85:
        gaps.append('GKE compliance below 85%')
    if quality_assessment.get('performance_score', 0) < 80:
        gaps.append('Performance standards not met')
    return gaps
