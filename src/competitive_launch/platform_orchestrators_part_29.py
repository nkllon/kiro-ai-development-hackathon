from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _generate_cost_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate cost optimization recommendations."""
        return ['Consider right-sizing instances based on actual usage', 'Implement spot instances for non-critical workloads', 'Optimize scheduling for cost-effective resource utilization']

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

