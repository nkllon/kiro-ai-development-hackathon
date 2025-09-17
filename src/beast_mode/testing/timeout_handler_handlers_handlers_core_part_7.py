from src.rm_ddd.core.health import ModuleHealth

def apply_graceful_degradation(self, operation_id: str, degradation_level: int=1) -> Dict[str, Any]:
    """
        Apply graceful degradation to an operation
        Requirements: 1.4 - Graceful degradation when analysis exceeds time limits
        """
    try:
        self.logger.warning(f'Applying graceful degradation level {degradation_level} to operation {operation_id}')
        timeout_event = TimeoutEvent(operation_id=operation_id, timeout_type='graceful', timestamp=datetime.now(), elapsed_seconds=self._get_operation_elapsed_time(operation_id), strategy_applied=f'degradation_level_{degradation_level}', degradation_level=degradation_level)
        self.timeout_events.append(timeout_event)
        self.graceful_timeouts += 1
        if degradation_level <= self.timeout_config.max_degradation_levels:
            degradation_strategy = self.degradation_strategies.get(degradation_level)
            if degradation_strategy:
                degradation_result = degradation_strategy(operation_id)
                if degradation_result.get('success', False):
                    self.successful_degradations += 1
                    timeout_event.operation_completed = True
                return degradation_result
        return self._apply_hard_timeout(operation_id)
    except Exception as e:
        self.logger.error(f'Graceful degradation failed for operation {operation_id}: {e}')
        return {'success': False, 'error': str(e), 'degradation_level': degradation_level, 'fallback_applied': 'hard_timeout'}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

