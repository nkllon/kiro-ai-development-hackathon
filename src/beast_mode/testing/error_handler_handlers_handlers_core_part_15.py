from src.rm_ddd.core.health import ModuleHealth

def _create_error_context(self, error: Exception, component: str, operation: str, duration: float=0.0, context_data: Optional[Dict[str, Any]]=None) -> ErrorContext:
    """Create comprehensive error context"""
    error_id = f'error_{int(time.time())}_{component}_{operation}'
    category = self._categorize_error(error)
    severity = self._assess_error_severity(error, category)
    context = ErrorContext(error_id=error_id, timestamp=datetime.now(), severity=severity, category=category, error_message=str(error), stack_trace=traceback.format_exc(), component=component, operation=operation, context_data=context_data or {})
    self.error_history.append(context)
    if len(self.error_history) > 100:
        self.error_history = self.error_history[-100:]
    return context

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

