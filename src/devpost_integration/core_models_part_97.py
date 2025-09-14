from src.rm_ddd.core.health import ModuleHealth

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Sync operation {self.operation_id}: {operation}')
