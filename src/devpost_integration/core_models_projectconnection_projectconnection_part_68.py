
def update_progress(self, progress: float) -> bool:
    """Update operation progress."""
    try:
        if 0 <= progress <= 1:
            self.progress = progress
            self._update_metrics('update_progress')
            return True
        else:
            logger.warning(f'Invalid progress value: {progress}')
            return False
    except Exception as e:
        logger.error(f'Failed to update progress: {e}')
        self._errors += 1
        return False
