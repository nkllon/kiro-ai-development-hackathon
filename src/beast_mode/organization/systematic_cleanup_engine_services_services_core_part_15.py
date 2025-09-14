from src.rm_ddd.core.health import ModuleHealth

class IdentifysystematicviolationsClass:
    """Auto-generated class for functions."""

    def _identify_systematic_violations(self, file_analyses: List[FileAnalysis]) -> List[Dict[str, Any]]:
    """Identify systematic violations requiring immediate attention"""
    violations = []
    for analysis in file_analyses:
    if analysis.cleanup_priority in [CleanupPriority.CRITICAL, CleanupPriority.HIGH]:
    violations.append({'file': str(analysis.file_path), 'violation_type': analysis.category.value, 'priority': analysis.cleanup_priority.value, 'systematic_impact': analysis.systematic_impact, 'recommended_action': f'Move to {analysis.recommended_location}'})
    return violations

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

