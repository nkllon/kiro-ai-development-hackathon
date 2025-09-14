from src.rm_ddd.core.health import ModuleHealth

    def process_input(self, input_data: bytes, format_type: str='auto') -> ProcessedInput:
        """Process stdin input based on format"""
        if format_type == 'auto':
            format_type = self.detect_format(input_data)
        processor = self.formats.get(format_type, self.process_text_input)
        return processor(input_data)

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

