from src.rm_ddd.core.health import ModuleHealth

    def add_error(self, error_message: str, field: str = None) -> None:
        """Add validation error."""
        try:
            error = {
                "message": error_message,
                "field": field,
                "timestamp": datetime.now().isoformat()
            }
            self.errors.append(error)
            self.is_valid = False
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to add error: {e}")
            self._errors += 1
    