from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _generate_risk_mitigation_plan(self, delay_risk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate risk mitigation plan for deadline management."""
        return [{'risk': 'behind_schedule', 'mitigation': 'parallel_execution', 'contingency': 'scope_reduction'}, {'risk': 'resource_constraints', 'mitigation': 'emergency_resource_allocation', 'contingency': 'priority_focus'}, {'risk': 'quality_degradation', 'mitigation': 'systematic_quality_gates', 'contingency': 'post_deadline_improvement'}]

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

