
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
    """Information about a registered RM module."""
    module_id: str
    module: 'ReflectiveModuleBase'
    registration_time: datetime
    last_health_check: Optional[datetime] = None
    last_health_status: Optional['ModuleHealth'] = None
    capabilities: List[ModuleCapability] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)


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