from src.rm_ddd.core.health import ModuleHealth

class CalculatercaconfidenceClass:
    """Auto-generated class for functions."""

    def _calculate_rca_confidence(self, analysis: ComprehensiveAnalysisResult, root_causes: List[RootCause], validations: List[ValidationResult]) -> float:
    """Calculate overall RCA confidence score"""
    analysis_confidence = analysis.analysis_confidence
    root_cause_confidence = sum((rc.confidence_score for rc in root_causes)) / max(1, len(root_causes))
    validation_confidence = sum((vr.confidence_score for vr in validations)) / max(1, len(validations))
    return (analysis_confidence + root_cause_confidence + validation_confidence) / 3

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

