from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _setup_emergency_monitoring(self, delay_risk: Dict[str, Any]) -> Dict[str, Any]:
        """Set up emergency monitoring for deadline management."""
        return {'active': True, 'monitoring_frequency': 'hourly', 'alert_thresholds': ['behind_schedule', 'resource_constraints', 'quality_degradation'], 'escalation_protocols': ['immediate_notification', 'emergency_meeting']}

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

