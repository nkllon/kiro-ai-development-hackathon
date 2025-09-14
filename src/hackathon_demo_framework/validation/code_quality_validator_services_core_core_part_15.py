from src.rm_ddd.core.health import ModuleHealth

class GeneraterecommendationsClass:
    """Auto-generated class for functions."""

    def _generate_recommendations(self, issues: List[CodeQualityIssue], scores: Dict[str, float]) -> List[str]:
    """Generate improvement recommendations based on issues and scores."""
    recommendations = []
    if scores['complexity'] < 70:
    recommendations.append('Reduce code complexity by breaking down complex functions')
    if scores['documentation'] < 80:
    recommendations.append('Improve documentation coverage with comprehensive docstrings')
    if scores['maintainability'] < 70:
    recommendations.append('Improve maintainability by reducing code duplication')
    if scores['style'] < 80:
    recommendations.append('Improve code style consistency with automated formatting')
    critical_issues = [i for i in issues if i.severity == 'critical']
    if critical_issues:
    recommendations.insert(0, f'Fix {len(critical_issues)} critical security/quality issues immediately')
    security_issues = [i for i in issues if i.issue_type == CodeQualityMetric.SECURITY]
    if security_issues:
    recommendations.append('Review and address security vulnerabilities')
    return recommendations[:5]

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

