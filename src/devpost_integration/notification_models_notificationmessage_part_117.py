from src.rm_ddd.core.health import ModuleHealth

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'message_id': self.message_id, 'status': self.status, 'recipient_count': len(self.recipients), 'priority': self.priority, 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

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

