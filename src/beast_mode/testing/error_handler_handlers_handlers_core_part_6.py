from src.rm_ddd.core.health import ModuleHealth

def handle_rca_operation(self, operation_name: str, component: str='unknown'):
    """
        Context manager for handling RCA operations with comprehensive error handling
        Requirements: 1.1, 1.4 - Comprehensive error handling with automatic retry
        """
    operation_id = f'{operation_name}_{int(time.time())}'
    start_time = time.time()
    try:
        self.logger.info(f'Starting RCA operation: {operation_name} on {component}')
        self._check_component_health(component)
        yield operation_id
        duration = time.time() - start_time
        self._record_successful_operation(component, operation_name, duration)
    except Exception as e:
        duration = time.time() - start_time
        error_context = self._create_error_context(error=e, component=component, operation=operation_name, duration=duration)
        self._handle_operation_error(error_context)
        self.total_errors_handled += 1
        raise
