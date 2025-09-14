from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def generate_remediation_plan(self, gaps: Dict[str, Any]) -> List[str]:
    """
        Generate systematic remediation plan for functionality gaps.
        
        Args:
            gaps: Functionality gaps from analyze_functionality_gaps()
            
        Returns:
            Prioritized list of remediation steps
        """
    remediation_steps = []
    if gaps.get('broken_integrations'):
        remediation_steps.append('CRITICAL: Fix broken imports and integration issues')
        for issue in gaps['broken_integrations']:
            remediation_steps.append(f'  - Fix: {issue}')
    if gaps.get('incomplete_features'):
        remediation_steps.append('HIGH: Complete missing core features')
        for feature in gaps['incomplete_features']:
            remediation_steps.append(f'  - Implement: {feature}')
    if gaps.get('missing_tests'):
        remediation_steps.append('MEDIUM: Improve test coverage')
        for test_issue in gaps['missing_tests']:
            remediation_steps.append(f'  - Add: {test_issue}')
    if gaps.get('missing_documentation'):
        remediation_steps.append('MEDIUM: Complete documentation')
        for doc_issue in gaps['missing_documentation']:
            remediation_steps.append(f'  - Document: {doc_issue}')
    if gaps.get('performance_issues'):
        remediation_steps.append('LOW: Address performance issues')
        for perf_issue in gaps['performance_issues']:
            remediation_steps.append(f'  - Optimize: {perf_issue}')
    return remediation_steps

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

