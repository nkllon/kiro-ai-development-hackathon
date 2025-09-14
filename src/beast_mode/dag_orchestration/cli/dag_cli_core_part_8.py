from src.rm_ddd.core.health import ModuleHealth

def _get_bobby_verdict(orchestration_result: OrchestrationResult) -> str:
    """Get Bobby's systematic verdict on ecosystem consumption."""
    quality_score = orchestration_result.systematic_quality_score
    success_prob = orchestration_result.mvp_route.success_probability
    risk_count = len(orchestration_result.risk_assessment.risk_factors)
    if quality_score > 0.9 and success_prob > 0.8:
        return 'DELICIOUS - Bobby loves systematic ecosystems'
    elif quality_score > 0.8 and success_prob > 0.7:
        return 'TASTY - Bobby consumed it with systematic satisfaction'
    elif quality_score > 0.7 and success_prob > 0.6:
        return 'EDIBLE - Bobby digested it but recommends systematic improvements'
    elif quality_score > 0.6:
        return 'TOUGH - Bobby chewed through it with systematic determination'
    else:
        return 'INDIGESTIBLE - Bobby recommends systematic remediation'
