
    def remove_recipient(self, recipient: str) -> bool:
        """Remove recipient from message."""
        try:
            if recipient in self.recipients:
                self.recipients.remove(recipient)
                self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to remove recipient: {e}')
            self._errors += 1
            return False
