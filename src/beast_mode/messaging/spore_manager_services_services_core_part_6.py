from src.rm_ddd.core.health import ModuleHealth

class ListsporesClass:
    """Auto-generated class for functions."""

    def list_spores(self) -> List[Dict[str, Any]]:
    """
    List all available spores with their metadata

    Returns:
    List of spore metadata dictionaries
    """
    spores = []
    try:
    all_spore_names = set(self._spore_cache.keys())
    for metadata_file in self.metadata_dir.glob('*.json'):
    all_spore_names.add(metadata_file.stem)
    for spore_name in all_spore_names:
    spore_data = self.load_spore(spore_name)
    if spore_data:
    spores.append(spore_data['metadata'])
    spores.sort(key=lambda x: x['name'])
    except Exception as e:
    logger.error(f'Failed to list spores: {e}')
    return spores

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

