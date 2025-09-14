from src.rm_ddd.core.health import ModuleHealth


class ImportsporeClass:
    """Auto-generated class for functions."""

    def import_spore(self, import_path: str) -> Optional[str]:
    """
    Import a spore from a file

    Args:
    import_path: Path to the spore file to import

    Returns:
    str: Name of imported spore or None if failed
    """
    try:
    import_file = Path(import_path)
    if not import_file.exists():
    logger.error(f'Import file not found: {import_path}')
    return None
    with open(import_file, 'r') as f:
    spore_data = json.load(f)
    metadata = spore_data['metadata']
    implementation = spore_data['implementation']
    spore_name = self.save_spore(implementation, metadata)
    logger.info(f'Imported spore: {spore_name}')
    return spore_name
    except Exception as e:
    logger.error(f'Failed to import spore from {import_path}: {e}')
    return None

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

