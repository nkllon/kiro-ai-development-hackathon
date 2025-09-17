from src.rm_ddd.core.health import ModuleHealth

def _find_common_text_patterns(self, texts: List[str]) -> Dict[str, int]:
    """Find common patterns in a list of texts"""
    pattern_counts = {}
    for text in texts:
        words = text.lower().split()
        for word in words:
            if len(word) > 3:
                pattern_counts[word] = pattern_counts.get(word, 0) + 1
    return {pattern: count for pattern, count in pattern_counts.items() if count > 1}

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

