from src.rm_ddd.core.health import ModuleHealth

    def __init__(self):
        """Initialize debugging engine"""
        super().__init__(module_id="debuggingengine", version="1.0.0")
        register_module(self)
    