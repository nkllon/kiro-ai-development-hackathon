from src.rm_ddd.core.health import ModuleHealth

    def __init__(self):
        """Initialize performance profiler"""
        super().__init__(module_id="performanceprofiler", version="1.0.0")
        register_module(self)
    