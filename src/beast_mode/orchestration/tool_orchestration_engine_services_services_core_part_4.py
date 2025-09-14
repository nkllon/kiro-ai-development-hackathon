from src.rm_ddd.core.health import ModuleHealth

def get_health_indicators(self) -> Dict[str, Any]:
    """Detailed health metrics for tool orchestration"""
    return {'orchestration_status': {'total_tools': len(self.tools_registry), 'healthy_tools': len([t for t in self.tool_health_cache.values() if t == ToolStatus.HEALTHY]), 'failed_tools': len([t for t in self.tool_health_cache.values() if t == ToolStatus.FAILED]), 'success_rate': self._calculate_success_rate()}, 'decision_framework': {'confidence_distribution': self.orchestration_metrics['decision_confidence_distribution'], 'intelligence_engine_healthy': self.intelligence_engine.is_healthy(), 'rca_engine_healthy': self.rca_engine.is_healthy(), 'multi_perspective_engine_healthy': self.multi_perspective_engine.is_healthy()}, 'performance_metrics': {'total_orchestrations': self.orchestration_metrics['total_orchestrations'], 'average_execution_time': self.orchestration_metrics['average_execution_time_ms'], 'tools_repaired': self.orchestration_metrics['tools_repaired'], 'fallbacks_used': self.orchestration_metrics['fallbacks_used']}}

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

