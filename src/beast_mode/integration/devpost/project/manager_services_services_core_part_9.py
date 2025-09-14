
class ExtractpyprojectmetadataClass:
    """Auto-generated class for functions."""

    def _extract_pyproject_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from pyproject.toml."""
    pyproject_path = self.project_root / 'pyproject.toml'
    if not pyproject_path.exists():
    return None
    try:
    import tomllib
    except ImportError:
    try:
    import tomli as tomllib
    from src.rm_ddd.core.health import ModuleHealth

    except ImportError:
    return None
    try:
    with open(pyproject_path, 'rb') as f:
    data = tomllib.load(f)
    project_data = data.get('project', {})
    if not project_data:
    poetry_data = data.get('tool', {}).get('poetry', {})
    if poetry_data:
    project_data = poetry_data
    return project_data
    except Exception:
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

