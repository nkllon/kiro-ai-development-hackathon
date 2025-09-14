from src.rm_ddd.core.health import ModuleHealth

class CreateemptyreportClass:
    """Auto-generated class for functions."""

    def _create_empty_report(self, reason: str) -> CodeQualityReport:
    """Create an empty report with error information."""
    return CodeQualityReport(overall_score=0.0, complexity_score=0.0, maintainability_score=0.0, documentation_score=0.0, style_score=0.0, security_score=0.0, performance_score=0.0, total_issues=1, critical_issues=1, major_issues=0, minor_issues=0, issues=[CodeQualityIssue(file_path='', line_number=1, issue_type=CodeQualityMetric.MAINTAINABILITY, severity='critical', message=reason, suggestion='Ensure project has analyzable Python source files')], recommendations=[reason], files_analyzed=0, lines_of_code=0)

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

