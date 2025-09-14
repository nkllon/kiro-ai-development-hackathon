from src.rm_ddd.core.health import ModuleHealth

def _detect_failure_correlations(self, basic_groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[TestFailureData]]:
    """Detect correlations within and across basic groups"""
    correlated_groups = {}
    for group_name, group_failures in basic_groups.items():
        if len(group_failures) <= 1:
            correlated_groups[group_name] = group_failures
            continue
        correlation_matrix = self._build_correlation_matrix(group_failures)
        subgroups = self._split_by_correlation(group_failures, correlation_matrix)
        for i, subgroup in enumerate(subgroups):
            subgroup_name = f'{group_name}_corr_{i}' if len(subgroups) > 1 else group_name
            correlated_groups[subgroup_name] = subgroup
    return correlated_groups

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

