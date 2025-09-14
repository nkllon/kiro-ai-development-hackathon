
def _apply_hard_timeout(self, operation_id: str) -> Dict[str, Any]:
    """Apply hard timeout termination"""
    try:
        timeout_event = TimeoutEvent(operation_id=operation_id, timeout_type='hard', timestamp=datetime.now(), elapsed_seconds=self._get_operation_elapsed_time(operation_id), strategy_applied='hard_termination')
        self.timeout_events.append(timeout_event)
        self._cleanup_operation_timeouts(operation_id)
        return {'success': False, 'timeout_type': 'hard', 'action': 'operation_terminated', 'elapsed_seconds': timeout_event.elapsed_seconds, 'message': f'Operation {operation_id} terminated due to hard timeout'}
    except Exception as e:
        self.logger.error(f'Hard timeout application failed for operation {operation_id}: {e}')
        return {'success': False, 'error': str(e), 'action': 'termination_failed'}
