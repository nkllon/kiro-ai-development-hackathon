from src.rm_ddd.core.health import ModuleHealth

class DiscoversourcefilesClass:
    """Auto-generated class for functions."""

    def _discover_source_files(self) -> List[Path]:
    """Discover Python source files to analyze."""
    source_files = []
    for pattern in self.source_patterns:
    files = list(self.project_path.rglob(pattern))
    source_files.extend(files)
    filtered_files = []
    for file_path in source_files:
    should_exclude = False
    for exclude_pattern in self.exclude_patterns:
    if file_path.match(exclude_pattern):
    should_exclude = True
    break
    if not should_exclude and file_path.is_file():
    filtered_files.append(file_path)
    return filtered_files

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

