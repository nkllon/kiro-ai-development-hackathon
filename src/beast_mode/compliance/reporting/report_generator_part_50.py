from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _format_appendix(self, analysis_result: ComplianceAnalysisResult) -> str:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Format appendix with technical details."""
        sections = ['### Technical Details', f'- Analysis Timestamp: {analysis_result.analysis_timestamp}', f'- Commits Analyzed: {len(analysis_result.commits_analyzed)}', f'- Overall Compliance Score: {analysis_result.overall_compliance_score:.2f}', '', '### Issue Summary by Severity']
        all_issues = self._collect_all_issues(analysis_result)
        severity_counts = {}
        for issue in all_issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        for severity in IssueSeverity:
            count = severity_counts.get(severity, 0)
            sections.append(f'- {severity.value.title()}: {count}')
        return '\n'.join(sections)

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

