from src.rm_ddd.core.health import ModuleHealth

    def __init__(self) -> Any:
        """Initialize the remediation guide with templates and known issues."""
        self.remediation_templates = self._initialize_remediation_templates()
        self.phase2_failing_tests = self._initialize_phase2_failing_tests()
        self.common_patterns = self._initialize_common_patterns()

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

