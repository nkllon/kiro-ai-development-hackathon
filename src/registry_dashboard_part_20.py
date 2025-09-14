from datetime import datetime
from typing import Dict, List, Any

    def generate_registry_report(self) -> str:
        """Generate a comprehensive registry report."""
        status = self.get_registry_status()
        
        report = f"""
📋 BEAST MODE FRAMEWORK REGISTRY DASHBOARD
==========================================

Registry Health: {status['registry_health_percentage']:.1f}%
Total Registered: {status['total_registered']}
Healthy Modules: {status['healthy_modules']}
Unhealthy Modules: {status['unhealthy_modules']}

Last Update: {status['last_update']}

Registered Modules:
"""
        
        for module_id, module_data in self.registered_modules.items():
            report += f"""
  {module_id}:
    Version: {module_data.get('version', 'unknown')}
    Class: {module_data.get('class_name', 'unknown')}
    File: {module_data.get('file_path', 'unknown')}
    Health: {module_data.get('health_status', 'unknown')}
    Capabilities: {', '.join(module_data.get('capabilities', []))}
    Dependencies: {', '.join(module_data.get('dependencies', []))}
    Last Updated: {module_data.get('last_updated', 'unknown')}
"""
        
        return report
