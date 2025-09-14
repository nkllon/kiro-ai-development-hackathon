from src.rm_ddd.core.health import ModuleHealth

def reset_metrics(self) -> None:
    """Reset module metrics"""
    self._metrics = {'operations_count': 0, 'last_operation_time': None, 'error_count': 0, 'success_rate': 1.0, 'metadata_updates': 0}
    self._logger.info('Metrics reset successfully')
