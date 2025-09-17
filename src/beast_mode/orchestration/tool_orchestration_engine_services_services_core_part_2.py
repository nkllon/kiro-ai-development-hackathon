from src.rm_ddd.core.health import ModuleHealth

def get_module_status(self) -> Dict[str, Any]:
    """Tool orchestration engine operational status"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'registered_tools': len(self.tools_registry), 'healthy_tools': len([t for t in self.tool_health_cache.values() if t == ToolStatus.HEALTHY]), 'total_orchestrations': self.orchestration_metrics['total_orchestrations'], 'success_rate': self._calculate_success_rate(), 'average_execution_time_ms': self.orchestration_metrics['average_execution_time_ms'], 'project_root': str(self.project_root)}

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

