from src.rm_ddd.core.health import ModuleHealth

class GetmetricsClass:
    """Auto-generated class for functions."""

    def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {
    "operation_count": self._operation_count,
    "error_count": self._errors,
    "validation_errors": len(self.errors),
    "validation_warnings": len(self.warnings),
    "is_valid": self.is_valid,
    "validation_time": self.validation_time.isoformat()
    }

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

