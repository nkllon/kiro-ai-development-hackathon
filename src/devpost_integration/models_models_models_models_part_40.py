
    def reset_metrics(self) -> None:
        """Reset module metrics"""
        self._metrics = {'operations_count': 0, 'last_operation_time': None, 'error_count': 0, 'success_rate': 1.0, 'previews_generated': 0, 'preview_errors': 0}
        self._logger.info('Metrics reset successfully')
