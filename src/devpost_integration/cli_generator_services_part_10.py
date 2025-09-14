from src.rm_ddd.core.health import ModuleHealth

    def process_text_input(self, input_data: bytes) -> ProcessedInput:
        """Process text input from stdin"""
        try:
            text = input_data.decode('utf-8')
            lines = text.strip().split('\n') if text.strip() else []
            return ProcessedInput(format='text', data=lines, success=True)
        except UnicodeDecodeError as e:
            return ProcessedInput(format='text', data=None, success=False, error=str(e))

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

