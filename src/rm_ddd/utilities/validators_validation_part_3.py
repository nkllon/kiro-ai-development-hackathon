from src.rm_ddd.core.health import ModuleHealth

def validate_ubiquitous_language(obj: Any, term_mapping: Dict[str, str]) -> ValidationResult:
    """Validate ubiquitous language usage."""
    result = ValidationResult(is_valid=True)
    class_name = obj.__class__.__name__
    if class_name.lower() not in [term.lower() for term in term_mapping.values()]:
        result.add_warning(f"Class name '{class_name}' not found in ubiquitous language mapping")
    return result

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

