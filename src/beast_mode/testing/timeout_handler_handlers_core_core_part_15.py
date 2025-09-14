from src.rm_ddd.core.health import ModuleHealth

def _handle_graceful_timeout(self, operation_id: str) -> None:
    """Handle graceful timeout"""
    try:
        self.logger.warning(f'Operation {operation_id} exceeded graceful timeout ({self.timeout_config.graceful_timeout_seconds}s)')
        if self.timeout_config.enable_progressive_degradation:
            self.apply_graceful_degradation(operation_id, degradation_level=1)
        else:
            self._apply_hard_timeout(operation_id)
    except Exception as e:
        self.logger.error(f'Graceful timeout handling failed for operation {operation_id}: {e}')
