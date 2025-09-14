from src.rm_ddd.core.health import ModuleHealth

    def register_pattern(self, pattern: CommandPattern) -> None:
        """Register a command pattern for validation."""
        key = f'{pattern.verb}_{pattern.noun}'
        self.command_patterns[key] = pattern
        self.update_activity()

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

