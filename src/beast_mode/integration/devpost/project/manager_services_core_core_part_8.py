from src.rm_ddd.core.health import ModuleHealth

def _extract_package_json_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from package.json."""
    package_json_path = self.project_root / 'package.json'
    if not package_json_path.exists():
        return None
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
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

