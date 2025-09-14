from src.rm_ddd.core.health import ModuleHealth

def _extract_query_filters(self, query: str) -> Dict[str, Any]:
    """Extract filters from the query"""
    filters = {}
    category_patterns = ['\\bin\\s+(\\w+)\\s+category\\b', '\\b(\\w+)\\s+category\\b', '\\btype\\s+(\\w+)\\b']
    for pattern in category_patterns:
        matches = re.findall(pattern, query)
        if matches:
            filters['category'] = matches[0]
    status_patterns = ['\\b(healthy|degraded|failed)\\s+domains?\\b', '\\bdomains?\\s+that\\s+are\\s+(healthy|degraded|failed)\\b']
    for pattern in status_patterns:
        matches = re.findall(pattern, query)
        if matches:
            filters['status'] = matches[0]
    complexity_patterns = ['\\b(simple|complex|high|low)\\s+complexity\\b', '\\bcomplexity\\s+(above|below|over|under)\\s+(\\d+(?:\\.\\d+)?)\\b']
    for pattern in complexity_patterns:
        matches = re.findall(pattern, query)
        if matches:
            if isinstance(matches[0], tuple):
                filters['complexity_threshold'] = float(matches[0][1])
                filters['complexity_operator'] = matches[0][0]
            else:
                filters['complexity_level'] = matches[0]
    return filters

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

