
def _create_timeout_context(self, operation_id: str) -> Dict[str, Any]:
    """Create timeout context for operation"""
    return {'operation_id': operation_id, 'timeout_config': self.timeout_config, 'start_time': datetime.now(), 'check_timeout': lambda: self._check_operation_timeout(operation_id), 'request_degradation': lambda level=1: self.apply_graceful_degradation(operation_id, level)}
