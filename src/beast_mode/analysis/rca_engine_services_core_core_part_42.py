from src.rm_ddd.core.health import ModuleHealth

class AnalyzepermissionsClass:
    """Auto-generated class for functions."""

    def _analyze_permissions(self, failure: Failure) -> Dict[str, Any]:
    """Analyze permission-related issues"""
    perm_analysis = {}
    if 'PermissionError' in failure.error_message or 'Permission denied' in failure.error_message:
    perm_analysis['has_permission_error'] = True
    perm_analysis['error_details'] = failure.error_message
    try:
    perm_analysis['cwd_writable'] = os.access('.', os.W_OK)
    perm_analysis['cwd_readable'] = os.access('.', os.R_OK)
    except Exception as e:
    perm_analysis['permission_check_error'] = str(e)
    else:
    perm_analysis['has_permission_error'] = False
    return perm_analysis

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

