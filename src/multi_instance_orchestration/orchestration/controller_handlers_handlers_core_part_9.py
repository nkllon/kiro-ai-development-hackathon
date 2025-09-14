from src.rm_ddd.core.health import ModuleHealth

class CalculateoptimalinstancesClass:
    """Auto-generated class for functions."""

    def _calculate_optimal_instances(self, tasks: List[Task], parallel_groups: List[List[str]]) -> int:
    """Calculate optimal number of instances based on tasks and parallelism."""
    max_parallel = max((len(group) for group in parallel_groups)) if parallel_groups else 1
    optimal = min(max_parallel, self.config.instance_count, self.config.max_instances, len(tasks))
    return max(optimal, self.config.min_instances)

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

