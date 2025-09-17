from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _parse_compliance_output(self, output: str) -> Dict[str, Any]:
        """Parse compliance reporter output"""
        compliance_data = {
            'total_files': 0,
            'valid_files': 0,
            'error_files': 0,
            'compliance_percentage': 0.0
        }
        
        for line in output.split('\n'):
            if 'Total Files:' in line:
                compliance_data['total_files'] = int(line.split(':')[1].strip())
            elif 'Valid Files:' in line:
                compliance_data['valid_files'] = int(line.split(':')[1].strip())
            elif 'Error Files:' in line:
                compliance_data['error_files'] = int(line.split(':')[1].strip())
            elif 'Syntax Compliance:' in line:
                compliance_data['compliance_percentage'] = float(
                    line.split(':')[1].replace('%', '').strip()
                )
        
        return compliance_data

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

    