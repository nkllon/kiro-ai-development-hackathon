from src.rm_ddd.core.registry import register_module
class InterfaceMetadata(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
    """Get health indicators for this module."""
    return {
    "module_id": self.module_id,
    "status": self.health_status,
    "last_updated": self.last_updated,
    "capabilities_count": len(self.capabilities),
    "dependencies_count": len(self.dependencies)
    }

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

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
    """Interface metadata"""
    interface_id: str
    interface_name: str
    interface_type: InterfaceType
    version: str
    status: InterfaceStatus
    description: str
    domain_terms: List[str]
    capabilities: List[str]
    dependencies: List[str]
    file_path: str
    created_at: datetime
    last_modified: datetime
    created_by: str
    usage_count: int = 0
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None

    @dataclass
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

    register_module('InterfaceMetadata', self)