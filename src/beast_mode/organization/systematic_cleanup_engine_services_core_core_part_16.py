from src.rm_ddd.core.health import ModuleHealth

def _generate_systematic_recommendations(self, file_analyses: List[FileAnalysis], entropy_metrics: Dict[str, float]) -> List[str]:
    """Generate systematic recommendations for organizational improvement"""
    recommendations = []
    if entropy_metrics['entropy_score'] > 0.8:
        recommendations.append('CRITICAL: Implement immediate systematic cleanup - entropy exceeds acceptable levels')
    elif entropy_metrics['entropy_score'] > 0.5:
        recommendations.append('HIGH: Schedule systematic cleanup - significant organizational entropy detected')
    if entropy_metrics['systematic_compliance'] < 0.7:
        recommendations.append('HIGH: Address critical systematic violations immediately')
    categories = self._categorize_files_summary(file_analyses)
    if categories.get('temporary', 0) > 5:
        recommendations.append('MEDIUM: Implement automatic temporary file cleanup')
    if categories.get('unknown', 0) > 10:
        recommendations.append('MEDIUM: Enhance file categorization patterns')
    recommendations.extend(['Establish systematic file placement standards', 'Implement organizational entropy monitoring', 'Create systematic cleanup automation', 'Add vibe coding compensation procedures'])
    return recommendations

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

