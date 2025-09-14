from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class ValidateinterfacesClass:
    """Auto-generated class for functions."""

    def _validate_interfaces(self) -> Dict[str, Any]:
    """Validate API and interface definitions."""
    interface_results = {'defined_interfaces': [], 'missing_interfaces': [], 'interface_score': 0.0, 'errors': []}
    try:
    source_files = list(self.project_path.rglob('src/**/*.py'))
    source_files.extend([f for f in self.project_path.rglob('*.py') if not f.name.startswith('test_')])
    total_interfaces = 0
    documented_interfaces = 0
    for source_file in source_files:
    try:
    with open(source_file, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())
    for node in ast.walk(tree):
    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
    total_interfaces += 1
    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
    documented_interfaces += 1
    interface_results['defined_interfaces'].append(f'{source_file.name}::{node.name}')
    else:
    interface_results['missing_interfaces'].append(f'{source_file.name}::{node.name} (missing docstring)')
    except Exception as e:
    interface_results['errors'].append(f'Interface analysis error {source_file}: {e}')
    if total_interfaces > 0:
    interface_results['interface_score'] = documented_interfaces / total_interfaces * 100
    else:
    interface_results['interface_score'] = 0.0
    except Exception as e:
    interface_results['errors'].append(f'Interface validation failed: {e}')
    return interface_results

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

