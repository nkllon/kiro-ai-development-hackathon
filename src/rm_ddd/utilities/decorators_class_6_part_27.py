from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def validate_language_consistency(self) -> ValidationResult:
        """Validate consistency with ubiquitous language."""
        result = ValidationResult(is_valid=True)
        class_name = self.__class__.__name__
        if class_name in term_mapping:
            definition = term_mapping[class_name]
            logger.debug(f'Validating {class_name} against definition: {definition}')
        return result
    cls._validate_language_consistency = validate_language_consistency

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

