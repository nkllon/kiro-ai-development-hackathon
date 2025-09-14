class RegistryDashboard(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
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
    
    print(f"
✅ Registry integration complete!")
    print(f"Implemented registry integration in {len(system.modules_needing_registry)} modules")

if __name__ == "__main__":
    main()
