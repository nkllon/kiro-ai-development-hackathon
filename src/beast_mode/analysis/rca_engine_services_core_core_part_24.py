from src.rm_ddd.core.health import ModuleHealth

class CalculateanalysisconfidenceClass:
    """Auto-generated class for functions."""

    def _calculate_analysis_confidence(self, analysis_results: Dict[str, Any]) -> float:
    """Calculate confidence score for comprehensive analysis"""
    successful_analyses = sum((1 for result in analysis_results.values() if 'error' not in result))
    total_analyses = len(analysis_results)
    return successful_analyses / max(1, total_analyses)

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

