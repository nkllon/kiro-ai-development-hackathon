from src.rm_ddd.core.health import ModuleHealth

def _calculate_cross_group_correlation(self, group_a: List[TestFailureData], group_b: List[TestFailureData]) -> float:
    """Calculate correlation score between two groups"""
    if not group_a or not group_b:
        return 0.0
    total_similarity = 0.0
    comparisons = 0
    for failure_a in group_a:
        for failure_b in group_b:
            total_similarity += self._calculate_failure_similarity(failure_a, failure_b)
            comparisons += 1
    return total_similarity / comparisons if comparisons > 0 else 0.0

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

