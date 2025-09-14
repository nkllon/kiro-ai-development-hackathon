from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def export_validation_report(self, file_path: str):
        """Export validation report to file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'validation_summary': self.get_validation_summary(),
            'validation_history': [
                {
                    'component_name': report.component_name,
                    'timestamp': report.timestamp.isoformat(),
                    'overall_score': report.overall_score,
                    'results': report.results
                }
                for report in self.validation_history
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)

# Global instance for easy access
enhanced_validator = EnhancedValidationFramework()

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

