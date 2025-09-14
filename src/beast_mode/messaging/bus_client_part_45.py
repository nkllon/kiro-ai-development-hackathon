from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_active_collaboration_sessions(self) -> List:
        """Get active collaboration sessions"""
        sessions = self.collaboration_scheduler.get_active_sessions()
        return [{'session_id': s.session_id, 'type': s.session_type.value, 'organizer': s.organizer_id, 'participants': s.participants, 'topic': s.topic, 'scheduled_start': s.scheduled_start.isoformat() if s.scheduled_start else None, 'actual_start': s.actual_start.isoformat() if s.actual_start else None, 'status': s.status.value} for s in sessions]
