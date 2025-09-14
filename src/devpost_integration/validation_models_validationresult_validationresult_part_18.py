
    def add_warning(self, warning_message: str, field: str = None) -> None:
        """Add validation warning."""
        try:
            warning = {
                "message": warning_message,
                "field": field,
                "timestamp": datetime.now().isoformat()
            }
            self.warnings.append(warning)
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to add warning: {e}")
            self._errors += 1
    