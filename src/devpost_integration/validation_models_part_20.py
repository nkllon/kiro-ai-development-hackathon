
    def clear_warnings(self) -> None:
        """Clear all validation warnings."""
        try:
            self.warnings.clear()
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to clear warnings: {e}")
            self._errors += 1
    