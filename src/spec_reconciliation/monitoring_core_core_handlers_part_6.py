from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, monitor_instance) -> Any:
        self.monitor = monitor_instance
        self.callback = callback_on_change
