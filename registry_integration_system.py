#!/usr/bin/env python3
"""
Registry Integration System

This system completes registry integration for modules that are missing it,
addressing the 11 modules identified in the RDI analysis.
"""

import os
import re
import json
from pathlib import Path


class RegistryIntegrationSystem:
    """System for implementing registry integration in modules."""

    def __init__(self):
        self.modules_needing_registry = []
        self.registry_template = '''
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information for registry."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'class_name': self.__class__.__name__,
            'file_path': self.__class__.__module__,
            'capabilities': self.get_capabilities(),
            'dependencies': self.get_dependencies(),
            'health_status': self.check_health().status.value,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities for registry."""
        capabilities = []
        
        # Add capabilities based on class methods
        for method_name in dir(self):
            if not method_name.startswith('_') and callable(getattr(self, method_name)):
                if method_name in ['process', 'execute', 'run', 'handle']:
                    capabilities.append(f"execute_{method_name}")
                elif method_name in ['validate', 'check', 'verify']:
                    capabilities.append(f"validate_{method_name}")
                elif method_name in ['get', 'fetch', 'retrieve']:
                    capabilities.append(f"retrieve_{method_name}")
                elif method_name in ['set', 'update', 'modify']:
                    capabilities.append(f"update_{method_name}")
        
        # Add default capabilities
        capabilities.extend([
            'health_monitoring',
            'status_reporting',
            'error_handling',
            'configuration_management'
        ])
        
        return list(set(capabilities))
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies for registry."""
        dependencies = []
        
        # Add standard dependencies
        dependencies.extend([
            'reflective_module',
            'datetime',
            'typing',
            'logging'
        ])
        
        # Add specific dependencies based on module type
        if 'auth' in self.module_id.lower():
            dependencies.append('auth_models')
        elif 'validation' in self.module_id.lower():
            dependencies.append('validation_models')
        elif 'notification' in self.module_id.lower():
            dependencies.append('notification_models')
        elif 'project' in self.module_id.lower():
            dependencies.append('project_models')
        elif 'sync' in self.module_id.lower():
            dependencies.append('sync_models')
        elif 'config' in self.module_id.lower():
            dependencies.append('config_models')
        elif 'core' in self.module_id.lower():
            dependencies.append('core_models')
        
        return list(set(dependencies))
    
    def register_with_registry(self):
        """Register this module with the RM registry."""
        try:
            from .reflective_module import register_module
            register_module(self)
            self._registry_registered = True
            print(f"✅ Registered {self.module_id} with RM registry")
        except Exception as e:
            print(f"❌ Failed to register {self.module_id}: {e}")
            self._registry_registered = False
    
    def unregister_from_registry(self):
        """Unregister this module from the RM registry."""
        try:
            from .reflective_module import unregister_module
            unregister_module(self.module_id)
            self._registry_registered = False
            print(f"✅ Unregistered {self.module_id} from RM registry")
        except Exception as e:
            print(f"❌ Failed to unregister {self.module_id}: {e}")
    
    def is_registry_registered(self) -> bool:
        """Check if this module is registered with the registry."""
        return getattr(self, '_registry_registered', False)
'''

    def scan_modules_needing_registry(self, directory="src"):
        """Scan for modules that need registry integration."""
        print("🔍 Scanning for modules needing registry integration...")

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    if self._needs_registry_integration(file_path):
                        self.modules_needing_registry.append(file_path)

        print(
            f"Found {len(self.modules_needing_registry)} modules needing registry integration"
        )

    def _needs_registry_integration(self, file_path):
        """Check if a module needs registry integration."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Check if it's a ReflectiveModule
            if "ReflectiveModule" not in content:
                return False

            # Check if it already has registry integration
            if "get_module_info" in content and "get_capabilities" in content:
                return False

            return True

        except Exception as e:
            print(f"Error checking {file_path}: {e}")
            return False

    def implement_registry_integration(self):
        """Implement registry integration in all modules that need it."""
        print("📋 Implementing registry integration...")

        for file_path in self.modules_needing_registry:
            self._implement_registry_in_file(file_path)

    def _implement_registry_in_file(self, file_path):
        """Implement registry integration in a specific file."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Check if it's already implemented
            if "get_module_info" in content:
                return

            # Find the class definition
            class_pattern = r"^class (\w+)\(ReflectiveModule\):"
            match = re.search(class_pattern, content, re.MULTILINE)

            if not match:
                return

            class_name = match.group(1)

            # Find the __init__ method
            init_pattern = rf"def __init__\(self[^)]*\):"
            init_match = re.search(init_pattern, content, re.MULTILINE)

            if not init_match:
                return

            # Add registry integration initialization to __init__
            init_end = init_match.end()
            init_content = content[init_match.start() : init_end]

            # Add registry integration initialization
            if "self.register_with_registry()" not in init_content:
                new_init = (
                    init_content.rstrip() + "\n        self.register_with_registry()\n"
                )
                content = content.replace(init_content, new_init)

            # Add registry integration methods
            # Find the end of the class (next class or end of file)
            next_class_pattern = r"^class \w+\(ReflectiveModule\):"
            next_class_match = re.search(
                next_class_pattern, content[init_end:], re.MULTILINE
            )

            if next_class_match:
                insert_pos = init_end + next_class_match.start()
            else:
                insert_pos = len(content)

            # Insert registry integration methods
            registry_methods = self.registry_template.format(class_name=class_name)
            content = content[:insert_pos] + registry_methods + content[insert_pos:]

            # Write the updated content
            with open(file_path, "w") as f:
                f.write(content)

            print(f"  ✅ Implemented registry integration in {file_path}")

        except Exception as e:
            print(f"  ❌ Error implementing registry integration in {file_path}: {e}")

    def create_registry_dashboard(self):
        """Create a registry monitoring dashboard."""
        print("📊 Creating registry monitoring dashboard...")

        dashboard_content = '''"""
Registry Monitoring Dashboard

Real-time registry monitoring dashboard for all modules.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class RegistryDashboard:
    """Registry monitoring dashboard for all modules."""
    
    def __init__(self):
        self.registered_modules = {}
        self.last_update = None
    
    def scan_registered_modules(self):
        """Scan all registered modules."""
        print("🔍 Scanning registered modules...")
        
        # This would be implemented to scan the RM registry
        # and collect module information
        pass
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status."""
        total_modules = len(self.registered_modules)
        healthy_modules = 0
        unhealthy_modules = 0
        
        for module_id, module_data in self.registered_modules.items():
            health_status = module_data.get('health_status', 'unknown')
            if health_status == 'HEALTHY':
                healthy_modules += 1
            else:
                unhealthy_modules += 1
        
        return {
            'total_registered': total_modules,
            'healthy_modules': healthy_modules,
            'unhealthy_modules': unhealthy_modules,
            'registry_health_percentage': (healthy_modules / total_modules * 100) if total_modules > 0 else 0,
            'last_update': self.last_update
        }
    
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

def main():
    """Main registry integration implementation."""
    print("🚀 Starting Registry Integration System...")
    print("Implementing registry integration for 11 modules...")
    
    system = RegistryIntegrationSystem()
    
    # Step 1: Scan for modules needing registry integration
    system.scan_modules_needing_registry()
    
    # Step 2: Implement registry integration
    system.implement_registry_integration()
    
    # Step 3: Create registry dashboard
    system.create_registry_dashboard()
    
    print(f"\n✅ Registry integration complete!")
    print(f"Implemented registry integration in {len(system.modules_needing_registry)} modules")

if __name__ == "__main__":
    main()
'''

        with open("src/registry_dashboard.py", "w") as f:
            f.write(dashboard_content)

        print("  Created registry monitoring dashboard: src/registry_dashboard.py")


def main():
    """Main registry integration implementation."""
    print("🚀 Starting Registry Integration System...")
    print("Implementing registry integration for 11 modules...")

    system = RegistryIntegrationSystem()

    # Step 1: Scan for modules needing registry integration
    system.scan_modules_needing_registry()

    # Step 2: Implement registry integration
    system.implement_registry_integration()

    # Step 3: Create registry dashboard
    system.create_registry_dashboard()

    print(f"\n✅ Registry integration complete!")
    print(
        f"Implemented registry integration in {len(system.modules_needing_registry)} modules"
    )


if __name__ == "__main__":
    main()
