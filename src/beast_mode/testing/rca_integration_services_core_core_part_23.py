from src.rm_ddd.core.health import ModuleHealth

def _split_by_correlation(self, failures: List[TestFailureData], correlation_matrix: List[List[float]]) -> List[List[TestFailureData]]:
    """Split failures into subgroups based on correlation matrix"""
    n = len(failures)
    if n <= 1:
        return [failures]
    threshold = 0.6
    groups = []
    assigned = [False] * n
    for i in range(n):
        if assigned[i]:
            continue
        group = [failures[i]]
        assigned[i] = True
        for j in range(i + 1, n):
            if not assigned[j] and correlation_matrix[i][j] > threshold:
                group.append(failures[j])
                assigned[j] = True
        groups.append(group)
    return groups

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

