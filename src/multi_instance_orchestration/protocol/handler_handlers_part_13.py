from src.rm_ddd.core.health import ModuleHealth

class ValidatecommandClass:
    """Auto-generated class for functions."""

    def validate_command(self, action: StructuredAction) -> ValidationResult:
    """Validate command syntax and permissions."""
    key = f'{action.verb}_{action.noun}'
    if key in self.command_patterns:
    pattern = self.command_patterns[key]
    return pattern.validate_action(action)
    else:
    return ValidationResult(is_valid=False, errors=[f'Unknown command pattern: {action.verb} {action.noun}'], suggestions=[f"Available patterns: {', '.join(self.command_patterns.keys())}"])

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

