from src.rm_ddd.core.health import ModuleHealth

def _determine_enhanced_intent(self, query: str, entities: Dict[str, List[str]]) -> str:
    """Determine query intent with enhanced logic"""
    pattern_indicators = ['pattern', 'file', 'path', '*.py', 'src/', 'tests/', '**']
    content_indicators = ['contains', 'content', 'indicator', 'includes', 'has']
    capability_indicators = ['tool', 'capability', 'can', 'does', 'supports', 'run', 'use', 'using']
    relationship_indicators = ['depend', 'similar', 'related', 'connect', 'link', 'couple']
    analysis_indicators = ['analyze', 'analysis', 'metrics', 'stats', 'health', 'report']
    pattern_count = sum((1 for indicator in pattern_indicators if indicator in query))
    content_count = sum((1 for indicator in content_indicators if indicator in query))
    capability_count = sum((1 for indicator in capability_indicators if indicator in query))
    relationship_count = sum((1 for indicator in relationship_indicators if indicator in query))
    analysis_count = sum((1 for indicator in analysis_indicators if indicator in query))
    if entities['patterns']:
        pattern_count += 2
    if entities['capabilities']:
        capability_count += 2
    scores = {'pattern_search': pattern_count, 'content_search': content_count, 'capability_search': capability_count, 'relationship_search': relationship_count, 'analysis_search': analysis_count}
    max_score = max(scores.values())
    if max_score > 0:
        return max(scores, key=scores.get)
    return 'general_search'

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

