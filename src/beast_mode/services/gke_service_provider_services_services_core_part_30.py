from src.rm_ddd.core.health import ModuleHealth

def _calculate_quality_improvement_potential(self, quality_assessment: Dict[str, Any]) -> Dict[str, float]:
    """Calculate potential for quality improvement"""
    current_score = self._calculate_overall_quality_score(quality_assessment)
    target_score = 95.0
    return {'current_quality_score': current_score, 'target_quality_score': target_score, 'improvement_potential_percent': target_score - current_score, 'systematic_approach_benefit': 25.0, 'estimated_improvement_timeline_weeks': max(2, int((target_score - current_score) / 10))}
