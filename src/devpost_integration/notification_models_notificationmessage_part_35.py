
def disable_notifications(self) -> bool:
    """Disable notifications."""
    try:
        self.enabled = False
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to disable notifications: {e}')
        self._errors += 1
        return False
