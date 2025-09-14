from src.rm_ddd.core.health import ModuleHealth

def add_channel(self, channel: str) -> bool:
    """Add notification channel."""
    try:
        if channel not in self.channels:
            self.channels.append(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add channel: {e}')
        self._errors += 1
        return False
