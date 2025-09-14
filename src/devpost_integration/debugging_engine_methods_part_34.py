from src.rm_ddd.core.health import ModuleHealth

    def __init__(self):
        """Initialize debug info"""
        super().__init__(module_id="debuginfo", version="1.0.0")
        register_module(self)
    