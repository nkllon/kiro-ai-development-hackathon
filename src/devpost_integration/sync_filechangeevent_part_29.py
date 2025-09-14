from src.rm_ddd.core.health import ModuleHealth

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0
    self.records_processed = 0
    self.records_failed = 0
    self.success = True
    self.error_message = None
