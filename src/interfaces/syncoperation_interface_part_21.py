
    def cancel_sync(self) -> bool:
        """Cancel synchronization operation."""
        try:
            self.status = 'cancelled'
            self.end_time = datetime.now()
            self._update_metrics('cancel_sync')
            return True
        except Exception as e:
            logger.error(f'Failed to cancel sync: {e}')
            self._errors += 1
            return False
