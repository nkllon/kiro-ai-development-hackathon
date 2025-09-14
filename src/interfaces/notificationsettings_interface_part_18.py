from src.rm_ddd.core.health import ModuleHealth

    def enable_notifications(self) -> bool:
        """Enable notifications."""
        try:
            self.enabled = True
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to enable notifications: {e}')
            self._errors += 1
            return False
