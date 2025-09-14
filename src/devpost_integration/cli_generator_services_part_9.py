from src.rm_ddd.core.health import ModuleHealth

    def process_json_input(self, input_data: bytes) -> ProcessedInput:
        """Process JSON input from stdin"""
        try:
            data = json.loads(input_data.decode('utf-8'))
            return ProcessedInput(format='json', data=data, success=True)
        except json.JSONDecodeError as e:
            return ProcessedInput(format='json', data=None, success=False, error=str(e))

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

