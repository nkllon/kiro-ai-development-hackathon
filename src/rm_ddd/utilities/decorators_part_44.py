from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def validate_purity(self) -> ValidationResult:
        """Validate that service contains only domain logic."""
        result = ValidationResult(is_valid=True)
        for attr_name in dir(self):
            if not attr_name.startswith('_'):
                attr_value = getattr(self, attr_name)
                if hasattr(attr_value, '__module__'):
                    module_name = attr_value.__module__
                    if any((infra_pattern in module_name.lower() for infra_pattern in ['sqlalchemy', 'django', 'flask', 'requests', 'boto3'])):
                        result.add_error(f'Domain service has infrastructure dependency: {module_name}')
        return result
    cls._validate_purity = validate_purity

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

