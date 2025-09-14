from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def export_compliance_report(self, file_path: str):
        """Export compliance report to file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'compliance_report': self.get_compliance_report(),
            'metrics_history': [
                {
                    'timestamp': metrics.timestamp.isoformat(),
                    'compliance_percentage': metrics.compliance_percentage,
                    'compliance_level': metrics.compliance_level.value,
                    'total_files': metrics.total_files,
                    'valid_files': metrics.valid_files,
                    'error_files': metrics.error_files
                }
                for metrics in self.metrics_history
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)


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

# Global instance