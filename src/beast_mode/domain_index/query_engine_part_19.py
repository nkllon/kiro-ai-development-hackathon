from src.rm_ddd.core.health import ModuleHealth

class GeneratecontextualsuggestionsClass:
    """Auto-generated class for functions."""

    def _generate_contextual_suggestions(self, partial_query: str, partial_info: Dict[str, Any]) -> List[str]:
    """Generate suggestions based on query context"""
    suggestions = []
    for intent in partial_info['intent_indicators']:
    if intent == 'pattern':
    suggestions.extend([f'{partial_query} src/**/*.py', f'{partial_query} tests/**/*.py', f'{partial_query} *.yaml'])
    elif intent == 'capability':
    suggestions.extend([f'{partial_query} pytest', f'{partial_query} linting', f'{partial_query} formatting'])
    elif intent == 'relationship':
    suggestions.extend([f'{partial_query} core_domain', f'{partial_query} test_domain', f'{partial_query} api_domain'])
    if 'domain_name' in partial_info['entity_hints']:
    if self.registry_manager:
    all_domains = self.registry_manager.get_all_domains()
    for domain_name in list(all_domains.keys())[:5]:
    if domain_name.lower().startswith(partial_info['last_token'].lower()):
    suggestions.append(partial_query.rsplit(' ', 1)[0] + f' {domain_name}')
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

