
def remove_channel(self, channel: str) -> bool:
    """Remove notification channel."""
    try:
        if channel in self.channels:
            self.channels.remove(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove channel: {e}')
        self._errors += 1
        return False
