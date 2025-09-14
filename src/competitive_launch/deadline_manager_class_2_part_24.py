from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _generate_scope_optimization_plan(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scope optimization plan."""
        plan = {'reductions': [], 'implementation_priority': 'immediate', 'total_time_saved': 0, 'competitive_impact_preserved': 1.0}
        for opp in opportunities:
            if opp['priority'] == 'high':
                plan['reductions'].append(opp)
                plan['total_time_saved'] += opp['time_saved']
                plan['competitive_impact_preserved'] -= opp['competitive_impact']
        return plan

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

