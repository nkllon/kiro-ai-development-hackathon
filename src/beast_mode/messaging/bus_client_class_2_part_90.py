from src.rm_ddd.core.health import ModuleHealth

class GetactivecollaborationsessionsClass:
    """Auto-generated class for functions."""

    def get_active_collaboration_sessions(self) -> List:
    """Get active collaboration sessions"""
    sessions = self.collaboration_scheduler.get_active_sessions()
    return [{'session_id': s.session_id, 'type': s.session_type.value, 'organizer': s.organizer_id, 'participants': s.participants, 'topic': s.topic, 'scheduled_start': s.scheduled_start.isoformat() if s.scheduled_start else None, 'actual_start': s.actual_start.isoformat() if s.actual_start else None, 'status': s.status.value} for s in sessions]

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

