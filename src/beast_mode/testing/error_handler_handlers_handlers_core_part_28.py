
def _handle_operation_error(self, error_context: ErrorContext) -> None:
    """Handle operation error and update health metrics"""
    self.monitor_component_health(error_context.component, False, 0.0)
