from src.rm_ddd.core.registry import register_module

def _calculate_risk_level(self, findings: List[Finding]) -> str:
    """Calculate overall risk level based on findings"""
    if not findings:
        return 'low'
    critical_count = sum((1 for f in findings if f.severity == Severity.CRITICAL))
    high_count = sum((1 for f in findings if f.severity == Severity.HIGH))
    if critical_count > 0:
        return 'critical'
    elif high_count > 2:
        return 'high'
    elif high_count > 0:
        return 'medium'
    else:
        return 'low'
