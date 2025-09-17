from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_compliance_report(self) -> Dict[str, Any]:
        """Get comprehensive compliance report"""
        if not self.metrics_history:
            return {'message': 'No compliance history available'}
        
        latest = self.metrics_history[-1]
        
        return {
            'current_compliance': {
                'percentage': latest.compliance_percentage,
                'level': latest.compliance_level.value,
                'total_files': latest.total_files,
                'valid_files': latest.valid_files,
                'error_files': latest.error_files,
                'timestamp': latest.timestamp.isoformat()
            },
            'trend': self.get_compliance_trend(),
            'target_achieved': self.is_target_achieved(),
            'target_percentage': self.compliance_threshold,
            'history_length': len(self.metrics_history)
        }

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

    