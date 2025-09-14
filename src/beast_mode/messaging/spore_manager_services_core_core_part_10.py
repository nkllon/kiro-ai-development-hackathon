from src.rm_ddd.core.health import ModuleHealth

class SearchsporesClass:
    """Auto-generated class for functions."""

    def search_spores(self, query: str, tags: Optional[List[str]]=None) -> List[Dict[str, Any]]:
    """
    Search spores by name, description, or tags

    Args:
    query: Search query string
    tags: Optional list of tags to filter by

    Returns:
    List of matching spore metadata
    """
    results = []
    try:
    all_spores = self.list_spores()
    for spore in all_spores:
    query_match = query.lower() in spore['name'].lower() or query.lower() in spore['description'].lower()
    tag_match = True
    if tags:
    spore_tags = spore.get('tags', [])
    tag_match = any((tag in spore_tags for tag in tags))
    if query_match and tag_match:
    results.append(spore)
    except Exception as e:
    logger.error(f'Failed to search spores: {e}')
    return results

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

