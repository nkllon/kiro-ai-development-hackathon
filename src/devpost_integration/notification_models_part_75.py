from src.rm_ddd.core.health import ModuleHealth

def mark_as_sent(self) -> bool:
    """Mark message as sent."""
    try:
        self.status = 'sent'
        self.sent_at = datetime.now()
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to mark as sent: {e}')
        self._errors += 1
        return False
