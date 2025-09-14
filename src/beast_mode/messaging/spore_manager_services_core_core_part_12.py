from src.rm_ddd.core.health import ModuleHealth

class ExportsporeClass:
    """Auto-generated class for functions."""

    def export_spore(self, spore_name: str, export_path: str) -> bool:
    """
    Export a spore to a file for sharing

    Args:
    spore_name: Name of the spore to export
    export_path: Path to export the spore to

    Returns:
    bool: True if successful, False otherwise
    """
    try:
    spore_data = self.load_spore(spore_name)
    if not spore_data:
    return False
    export_file = Path(export_path)
    export_file.parent.mkdir(parents=True, exist_ok=True)
    with open(export_file, 'w') as f:
    json.dump(spore_data, f, indent=2, default=str)
    logger.info(f'Exported spore {spore_name} to {export_path}')
    return True
    except Exception as e:
    logger.error(f'Failed to export spore {spore_name}: {e}')
    return False

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

