from src.rm_ddd.core.health import ModuleHealth

def _generate_intelligent_suggestions(self, original_query: str, parsed_query: Dict[str, Any], results: List[Domain]) -> List[str]:
    """Generate intelligent query suggestions"""
    suggestions = []
    keywords = parsed_query.get('keywords', [])
    entities = parsed_query.get('entities', {})
    query_type = parsed_query.get('query_type', 'search')
    if len(results) == 0:
        suggestions.append(f"Try broader terms: {' OR '.join(keywords[:3])}")
        suggestions.append('Search for similar capabilities or patterns')
        if entities.get('domain_names'):
            suggestions.append(f"Check if domain '{entities['domain_names'][0]}' exists")
    elif len(results) > 20:
        suggestions.append('Add more specific filters to narrow results')
        if not parsed_query.get('filters'):
            suggestions.append('Try adding category or status filters')
    if keywords:
        primary_keyword = keywords[0]
        suggestions.append(f'Find domains similar to {primary_keyword}')
        suggestions.append(f'Show dependencies of {primary_keyword} domains')
        suggestions.append(f'Analyze {primary_keyword} domain relationships')
    if query_type == 'search':
        suggestions.append("Try relationship analysis: 'domains that depend on X'")
        suggestions.append("Try capability search: 'domains that can run tests'")
    if entities.get('capabilities'):
        cap = entities['capabilities'][0]
        suggestions.append(f'Find all domains using {cap}')
    if entities.get('patterns'):
        pattern = entities['patterns'][0]
        suggestions.append(f'Find domains with similar patterns to {pattern}')
    return suggestions[:self.suggestion_limit]

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

