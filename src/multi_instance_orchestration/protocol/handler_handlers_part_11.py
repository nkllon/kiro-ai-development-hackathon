from src.rm_ddd.core.health import ModuleHealth

    def _normalize_command_text(self, text: str) -> str:
        """Normalize command text for parsing."""
        replacements = {'\\bexecute\\b': 'run', '\\bhalt\\b': 'stop', '\\bin beast mode\\b': 'beast-mode', '\\bin parallel\\b': 'parallel', '\\ball running threads\\b': 'instances all', '\\bactive processes\\b': 'instances active', '\\bgracefully\\b': 'graceful'}
        normalized = text.lower().strip()
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        return normalized

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

