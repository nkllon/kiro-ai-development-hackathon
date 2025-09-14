from src.rm_ddd.core.registry import register_module
class AnalysisConfiguration(ReflectiveModule):
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
    """Configuration for analysis operations"""
    timeout_seconds: int = 300
    max_parallel_analyses: int = 4
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {'max_memory_mb': 1024, 'max_cpu_percent': 50, 'max_disk_io_mb': 100})
    analysis_thresholds: Dict[str, Any] = field(default_factory=lambda: {'max_file_size_lines': 200, 'complexity_threshold': 10.0, 'coverage_minimum': 0.8, 'performance_threshold_ms': 1000})
    safety_enabled: bool = True
    emergency_shutdown_enabled: bool = True

@dataclass(frozen=True)
    def __init__(self):

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        register_module('AnalysisConfiguration', self)