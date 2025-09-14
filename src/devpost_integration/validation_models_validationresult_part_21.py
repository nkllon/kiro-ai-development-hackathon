from src.rm_ddd.core.health import ModuleHealth

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "validation_time": self.validation_time.isoformat(),
            "errors": self.errors,
            "warnings": self.warnings
        }
    