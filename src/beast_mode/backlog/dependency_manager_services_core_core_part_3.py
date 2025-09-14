
def is_healthy(self) -> bool:
    """Health assessment based on performance and data consistency"""
    try:
        if not self._is_performance_healthy():
            return False
        if not self._validate_internal_consistency():
            return False
        return True
    except Exception as e:
        self.logger.error(f'Health check failed: {str(e)}')
        return False
