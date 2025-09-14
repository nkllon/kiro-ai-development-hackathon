from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _identify_scope_reduction_options(self, tasks: List[Dict[str, Any]], critical_path: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify scope reduction options with competitive impact analysis."""
        options = []
        for task in tasks:
            if task.get('optional', False) or task.get('nice_to_have', False):
                option = {'task_id': task.get('id', 'unknown'), 'description': task.get('description', 'Unknown task'), 'time_saved_days': task.get('estimated_duration_days', 1), 'competitive_impact_lost': task.get('competitive_impact', 0.5), 'reduction_type': 'optional_feature'}
                options.append(option)
        options.sort(key=lambda x: x['competitive_impact_lost'])
        return options

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

