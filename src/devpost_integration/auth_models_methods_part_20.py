from src.rm_ddd.core.health import ModuleHealth

    def __init__(self):
        """Initialize auth session"""
        super().__init__(module_id="authsession", version="1.0.0")
        register_module(self)
    