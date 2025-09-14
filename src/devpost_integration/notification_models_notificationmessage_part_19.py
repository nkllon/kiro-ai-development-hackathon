from src.rm_ddd.core.health import ModuleHealth

    def add_recipient(self, recipient: str) -> bool:
        """Add recipient to message."""
        try:
            if recipient not in self.recipients:
                self.recipients.append(recipient)
                self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to add recipient: {e}')
            self._errors += 1
            return False
