from src.rm_ddd.core.health import ModuleHealth

def _analyze_reliability_trends(self) -> Dict[str, Any]:
    """Analyze tool reliability trends"""
    return {'overall_reliability_trend': 'stable', 'most_reliable_tools': list(self.tool_metrics.keys())}
