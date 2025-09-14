from src.rm_ddd.core.health import ModuleHealth

def _rank_and_filter_results(self, domains: List[Domain], parsed_query: Dict[str, Any]) -> List[Domain]:
    """Apply ranking and filtering based on query modifiers"""
    modifiers = parsed_query.get('modifiers', [])
    sort_field = None
    sort_order = 'desc'
    for modifier in modifiers:
        if modifier.startswith('sort_by:'):
            sort_field = modifier.split(':')[1]
        elif modifier.startswith('order:'):
            sort_order = modifier.split(':')[1]
    if sort_field:
        if sort_field == 'name':
            domains.sort(key=lambda d: d.name, reverse=sort_order == 'desc')
        elif sort_field == 'complexity':
            pass
        elif sort_field == 'dependencies':
            domains.sort(key=lambda d: len(d.dependencies), reverse=sort_order == 'desc')
    for modifier in modifiers:
        if modifier.startswith('limit:'):
            limit = int(modifier.split(':')[1])
            domains = domains[:limit]
            break
    return domains

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

