from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_expected_completion(self, parallel_plan: Dict[str, Any], scope_optimization: Dict[str, Any]) -> datetime:
        """Calculate expected completion time with acceleration."""
        time_savings = parallel_plan.get('expected_time_savings', 0) + scope_optimization.get('time_saved_days', 0)
        days_saved = time_savings * 10
        return datetime.now() + timedelta(days=max(1, 10 - days_saved))

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

