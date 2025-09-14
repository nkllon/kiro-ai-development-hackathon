from src.rm_ddd.core.health import ModuleHealth

    def set_success(self, success: bool, error_message: str=None) -> None:
        """Set sync success status."""
        try:
            self.success = success
            if not success and error_message:
                self.error_message = error_message
            self._operation_count += 1
        except Exception as e:
            logger.error(f'Failed to set success status: {e}')
            self._errors += 1
