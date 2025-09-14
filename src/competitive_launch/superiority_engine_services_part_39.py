from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _load_baseline_data(self) -> Dict[str, Any]:
        """Load baseline data for calculations."""
        return {'industry_averages': {'test_coverage': 30.0, 'customer_satisfaction': 68.0, 'time_to_market': 12.0, 'technical_debt_score': 60.0}, 'systematic_benchmarks': {'test_coverage': 95.0, 'customer_satisfaction': 92.0, 'time_to_market': 6.0, 'technical_debt_score': 5.0}}

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

