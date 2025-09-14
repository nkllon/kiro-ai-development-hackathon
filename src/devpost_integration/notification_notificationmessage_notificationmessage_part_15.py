
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'message_id': self.message_id, 'status': self.status, 'recipient_count': len(self.recipients), 'priority': self.priority, 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}
