
def _cleanup_operation_callbacks(self, operation_id: str) -> None:
    """Clean up operation callbacks"""
    if operation_id in self.operation_callbacks:
        del self.operation_callbacks[operation_id]
