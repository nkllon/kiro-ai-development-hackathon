
def _handle_warning_timeout(self, operation_id: str) -> None:
    """Handle warning timeout"""
    try:
        self.timeout_warnings += 1
        self.logger.warning(f'Operation {operation_id} exceeded warning timeout ({self.timeout_config.warning_timeout_seconds}s)')
        timeout_event = TimeoutEvent(operation_id=operation_id, timeout_type='warning', timestamp=datetime.now(), elapsed_seconds=self.timeout_config.warning_timeout_seconds, strategy_applied='warning_logged')
        self.timeout_events.append(timeout_event)
    except Exception as e:
        self.logger.error(f'Warning timeout handling failed for operation {operation_id}: {e}')
