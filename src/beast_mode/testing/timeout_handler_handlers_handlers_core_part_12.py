from src.rm_ddd.core.health import ModuleHealth

def _cleanup_operation_timeouts(self, operation_id: str) -> None:
    """Clean up timeout handlers for completed operation"""
    try:
        if operation_id in self.active_timeouts:
            handlers = self.active_timeouts.pop(operation_id)
            for handler_type, timer in handlers.items():
                if timer.is_alive():
                    timer.cancel()
    except Exception as e:
        self.logger.error(f'Failed to cleanup timeouts for operation {operation_id}: {e}')
