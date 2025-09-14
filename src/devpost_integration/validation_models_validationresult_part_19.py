
    def clear_errors(self) -> None:
        """Clear all validation errors."""
        try:
            self.errors.clear()
            self.is_valid = True
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to clear errors: {e}")
            self._errors += 1
    