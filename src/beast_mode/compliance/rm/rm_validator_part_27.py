from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def check_standards(self, interface_data: Dict[str, Any]) -> List[str]:
        """Check compliance standards"""
        standards_checks = []
        
        # Check naming conventions
        if 'name' in interface_data:
            name = interface_data['name']
            if not name[0].isupper():
                standards_checks.append("Interface name should start with uppercase")
            if '_' in name and not name.isupper():
                standards_checks.append("Consider using CamelCase for interface names")
        
        # Check method naming
        if 'methods' in interface_data:
            for method in interface_data['methods']:
                if not method.startswith(('get_', 'set_', 'is_', 'has_', 'validate_', 'register_')):
                    standards_checks.append(f"Method '{method}' should follow naming conventions")
        
        return standards_checks

# Global compliance system instance
compliance_system = ComplianceSystem()
