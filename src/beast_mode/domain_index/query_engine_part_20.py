from src.rm_ddd.core.health import ModuleHealth

def _generate_completion_suggestions(self, partial_query: str) -> List[str]:
    """Generate word completion suggestions"""
    suggestions = []
    self._ensure_indexes_built()
    last_word = partial_query.split()[-1] if partial_query.split() else partial_query
    for pattern in self._pattern_index.keys():
        if pattern.startswith(last_word.lower()):
            completed_query = partial_query.rsplit(' ', 1)[0] + f' {pattern}' if ' ' in partial_query else pattern
            suggestions.append(completed_query)
    for indicator in self._content_index.keys():
        if indicator.startswith(last_word.lower()):
            completed_query = partial_query.rsplit(' ', 1)[0] + f' {indicator}' if ' ' in partial_query else indicator
            suggestions.append(completed_query)
    for capability in self._capability_index.keys():
        if capability.startswith(last_word.lower()):
            completed_query = partial_query.rsplit(' ', 1)[0] + f' {capability}' if ' ' in partial_query else capability
            suggestions.append(completed_query)
    return suggestions

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

