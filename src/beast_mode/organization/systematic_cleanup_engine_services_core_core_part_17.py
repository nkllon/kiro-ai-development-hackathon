
def _assess_cleanup_urgency(self, entropy_metrics: Dict[str, float]) -> str:
    """Assess urgency of systematic cleanup"""
    entropy_score = entropy_metrics['entropy_score']
    compliance_score = entropy_metrics['systematic_compliance']
    if entropy_score > 0.8 or compliance_score < 0.5:
        return 'CRITICAL: Immediate systematic intervention required'
    elif entropy_score > 0.5 or compliance_score < 0.7:
        return 'HIGH: Systematic cleanup should be prioritized'
    elif entropy_score > 0.3:
        return 'MEDIUM: Systematic cleanup recommended'
    else:
        return 'LOW: Organizational maintenance sufficient'
