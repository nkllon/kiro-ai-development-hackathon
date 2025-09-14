from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, config: Optional[Dict[str, Any]]=None):
        """Initialize contrast analyzer."""
        super().__init__(config)
        self.normal_text_threshold = self.get_threshold('contrast_normal', 4.5)
        self.large_text_threshold = self.get_threshold('contrast_large', 3.0)
        self.graphical_threshold = self.get_threshold('contrast_graphical', 3.0)
        self.large_text_size = self.get_threshold('large_text_size', 18)
        self.bold_large_text_size = self.get_threshold('bold_large_text_size', 14)


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