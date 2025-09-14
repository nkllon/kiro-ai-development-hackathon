from src.rm_ddd.core.health import ModuleHealth

def add_callback(self, event: str, callback: Callable):
    """Add callback for service events"""
    if event in self.callbacks:
        self.callbacks[event].append(callback)
