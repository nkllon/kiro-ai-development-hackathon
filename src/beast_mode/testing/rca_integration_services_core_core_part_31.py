from src.rm_ddd.core.health import ModuleHealth

def _analyze_error_pattern_correlations(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
    """Analyze error pattern correlations"""
    correlations = []
    error_groups = {}
    for failure in failures:
        error_key = self._extract_error_pattern(failure.error_message)
        if error_key not in error_groups:
            error_groups[error_key] = []
        error_groups[error_key].append(failure)
    for error_pattern, group_failures in error_groups.items():
        if len(group_failures) > 1:
            correlations.append({'type': 'error_pattern', 'pattern': error_pattern, 'failures': [f.test_name for f in group_failures], 'correlation_strength': min(1.0, len(group_failures) / len(failures))})
    return correlations

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

