
def _handle_hard_timeout(self, operation_id: str) -> None:
    """Handle hard timeout"""
    try:
        self.hard_timeouts += 1
        self.logger.error(f'Operation {operation_id} exceeded hard timeout ({self.timeout_config.hard_timeout_seconds}s)')
        self._apply_hard_timeout(operation_id)
    except Exception as e:
        self.logger.error(f'Hard timeout handling failed for operation {operation_id}: {e}')
