
def _stop_health_monitoring(self):
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Stop periodic health monitoring."""
    if self._health_check_task:
        self._health_check_task.cancel()
        logger.info('Stopped registry health monitoring')

@property