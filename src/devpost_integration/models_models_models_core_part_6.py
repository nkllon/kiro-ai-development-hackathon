from src.rm_ddd.core.health import ModuleHealth

def _identify_health_issues(self) -> List[str]:
    """Identify health issues"""
    issues = []
    if self._metrics['success_rate'] < 0.8:
        issues.append('Low success rate detected')
    if self._metrics['error_count'] > 10:
        issues.append('High error count detected')
    return issues
