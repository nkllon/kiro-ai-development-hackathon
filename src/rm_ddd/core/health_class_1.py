from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule
class ModuleHealth(ReflectiveModule):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
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
    """
    Comprehensive module health information.
    
    Contains all health-related data for an RM module including status,
    capabilities, performance metrics, and domain-specific health indicators.
    """
    status: ModuleStatus
    message: str
    capabilities: List['ModuleCapability']
    domain_health: Optional['DomainHealth'] = None
    health_indicators: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Optional[PerformanceMetrics] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_healthy(self) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Check if module is in a healthy state."""
        return self.status in [ModuleStatus.AVAILABLE, ModuleStatus.INITIALIZING]

    @property
    def is_degraded(self) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Check if module is in a degraded state."""
        return self.status == ModuleStatus.DEGRADED

    @property
    def is_unavailable(self) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Check if module is unavailable."""
        return self.status in [ModuleStatus.UNAVAILABLE, ModuleStatus.SHUTTING_DOWN]

    def to_dict(self) -> Dict[str, Any]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Convert health status to dictionary."""
        return {'status': self.status.value, 'message': self.message, 'is_healthy': self.is_healthy, 'is_degraded': self.is_degraded, 'is_unavailable': self.is_unavailable, 'capabilities': [cap.name for cap in self.capabilities], 'domain_health': self.domain_health.to_dict() if self.domain_health else None, 'health_indicators': self.health_indicators, 'performance_metrics': {'response_time_ms': self.performance_metrics.response_time_ms, 'throughput_per_second': self.performance_metrics.throughput_per_second, 'error_rate': self.performance_metrics.error_rate, 'cpu_usage_percent': self.performance_metrics.cpu_usage_percent, 'memory_usage_mb': self.performance_metrics.memory_usage_mb} if self.performance_metrics else None, 'timestamp': self.timestamp.isoformat()}


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

@dataclass