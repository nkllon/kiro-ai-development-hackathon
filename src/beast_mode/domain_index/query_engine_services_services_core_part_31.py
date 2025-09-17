from src.rm_ddd.core.health import ModuleHealth

def _extract_entities(self, query: str) -> Dict[str, List[str]]:
    """Extract named entities from the query"""
    entities = {'domain_names': [], 'patterns': [], 'capabilities': [], 'categories': [], 'tools': []}
    domain_patterns = ['\\b(\\w+_domain)\\b', '\\b(\\w+domain)\\b', '\\bdomain[_\\s]+(\\w+)\\b']
    for pattern in domain_patterns:
        matches = re.findall(pattern, query)
        entities['domain_names'].extend(matches)
    pattern_indicators = ['(\\*\\*?/[^/\\s]+)', '([^/\\s]+\\.\\w+)', '(src/[^/\\s]+)', '(tests?/[^/\\s]+)']
    for pattern in pattern_indicators:
        matches = re.findall(pattern, query)
        entities['patterns'].extend(matches)
    capability_keywords = ['pytest', 'unittest', 'test', 'testing', 'pylint', 'flake8', 'ruff', 'lint', 'linting', 'black', 'autopep8', 'format', 'formatting', 'mypy', 'type', 'typing', 'annotations', 'docker', 'kubernetes', 'deploy', 'deployment', 'api', 'rest', 'graphql', 'endpoint', 'database', 'sql', 'nosql', 'storage']
    for capability in capability_keywords:
        if capability in query:
            entities['capabilities'].append(capability)
    category_keywords = ['core', 'tools', 'infrastructure', 'demo', 'test', 'api', 'data']
    for category in category_keywords:
        if category in query:
            entities['categories'].append(category)
    return entities

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

