from src.rm_ddd.core.health import ModuleHealth

def _extract_readme_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from README files."""
    readme_patterns = ['README.md', 'README.rst', 'README.txt', 'README']
    for pattern in readme_patterns:
        readme_path = self.project_root / pattern
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8')
                return self._parse_readme_content(content, readme_path)
            except Exception:
                continue
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

