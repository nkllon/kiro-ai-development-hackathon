
def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'enabled': self.enabled, 'channel_count': len(self.channels), 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing)}
