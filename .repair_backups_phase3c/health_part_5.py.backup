from src.rm_ddd.core.health import ModuleHealth

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

    @property