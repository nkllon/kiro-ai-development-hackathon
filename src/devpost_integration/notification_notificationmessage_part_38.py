
def set_timing(self, timing: NotificationTiming) -> bool:
    """Set notification timing."""
    try:
        self.timing = timing
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set timing: {e}')
        self._errors += 1
        return False
