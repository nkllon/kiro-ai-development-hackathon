from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class CheckimporthealthClass:
    """Auto-generated class for functions."""

    def _check_import_health(self) -> List[str]:
    """Check for broken imports in the project."""
    import_issues = []
    try:
    source_files = []
    hackathon_src = self.project_path / 'src' / 'hackathon_demo_framework'
    if hackathon_src.exists():
    source_files = list(hackathon_src.rglob('*.py'))[:5]
    for source_file in source_files:
    try:
    with open(source_file, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())
    for node in ast.walk(tree):
    if isinstance(node, ast.Import):
    for alias in node.names:
    try:
    importlib.import_module(alias.name)
    except ImportError:
    import_issues.append(f'Cannot import {alias.name} in {source_file.name}')
    elif isinstance(node, ast.ImportFrom):
    if node.module:
    try:
    importlib.import_module(node.module)
    except ImportError:
    import_issues.append(f'Cannot import from {node.module} in {source_file.name}')
    except Exception as e:
    import_issues.append(f'Import analysis error in {source_file}: {e}')
    except Exception as e:
    import_issues.append(f'Import health check failed: {e}')
    return import_issues

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

