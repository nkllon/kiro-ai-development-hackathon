from src.rm_ddd.core.health import ModuleHealth

def get_message_summary(self) -> Dict[str, Any]:
    """Get message summary."""
    return {'message_id': self.message_id, 'title': self.title, 'content': self.content[:100] + '...' if len(self.content) > 100 else self.content, 'status': self.status, 'priority': self.priority, 'recipient_count': len(self.recipients), 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}
