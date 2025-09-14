
def _initialize_component_health(self) -> None:
    """Initialize health tracking for all monitored components"""
    for component in self.monitored_components:
        self._initialize_component_health_entry(component)
