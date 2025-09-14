from src.rm_ddd.core.health import ModuleHealth

def manage_operation_timeout(self, operation_id: str, operation_callback: Optional[Callable]=None):
    """
        Context manager for managing operation timeouts with graceful degradation
        Requirements: 1.4 - 30-second timeout with graceful degradation
        """
    self.total_operations += 1
    if operation_callback:
        self.operation_callbacks[operation_id] = operation_callback
    timeout_handlers = self._setup_timeout_handlers(operation_id)
    try:
        self.logger.info(f'Managing timeout for operation: {operation_id} (strategy: {self.timeout_config.strategy.value})')
        yield self._create_timeout_context(operation_id)
        self._cleanup_operation_timeouts(operation_id)
        self.logger.info(f'Operation {operation_id} completed within timeout limits')
    except Exception as e:
        self._cleanup_operation_timeouts(operation_id)
        self.logger.error(f'Operation {operation_id} failed: {e}')
        raise
    finally:
        self._cleanup_operation_callbacks(operation_id)
