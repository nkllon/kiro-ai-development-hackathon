
def _record_successful_operation(self, component: str, operation: str, duration: float) -> None:
    """Record successful operation for health monitoring"""
    self.monitor_component_health(component, True, duration * 1000)
