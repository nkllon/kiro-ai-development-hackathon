from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class ResolvepathconflictClass:
    """Auto-generated class for functions."""

    def resolve_path_conflict(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
    Resolve path conflicts by choosing the most appropriate representation.

    This method attempts to resolve conflicts between absolute and relative paths
    by choosing the representation that makes the most sense in context.

    Args:
    path: Path that may have conflicts
    base: Base directory for context

    Returns:
    Path: Resolved path in the most appropriate format

    Example:
    >>> PathNormalizer.resolve_path_conflict("src/main.py", "/project/root")
    PosixPath('src/main.py')  # Keeps relative if it makes sense
    """
    path_obj = Path(path)
    base_obj = Path(base)
    if not path_obj.is_absolute():
    potential_absolute = PathNormalizer.normalize_path(base_obj / path_obj)
    base_normalized = PathNormalizer.normalize_path(base_obj)
    try:
    potential_absolute.relative_to(base_normalized)
    return path_obj
    except ValueError:
    pass
    try:
    return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
    return PathNormalizer.normalize_path(path)


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

    @staticmethod