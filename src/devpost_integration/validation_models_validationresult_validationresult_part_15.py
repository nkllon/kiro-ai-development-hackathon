from src.rm_ddd.core.health import ModuleHealth

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {
            "operation_count": self._operation_count,
            "error_count": self._errors,
            "validation_errors": len(self.errors),
            "validation_warnings": len(self.warnings),
            "is_valid": self.is_valid,
            "validation_time": self.validation_time.isoformat()
        }
    