from src.rm_ddd.core.health import ModuleHealth

def validate_aggregate(self, aggregate: AggregateRoot) -> ValidationResult:
    """Validate an aggregate root."""
    result = ValidationResult(is_valid=True)
    entity_result = self.validate_entity(aggregate)
    result.merge(entity_result)
    for rule in self._rules['aggregate']:
        rule_result = rule.validate(aggregate)
        result.merge(rule_result)
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

