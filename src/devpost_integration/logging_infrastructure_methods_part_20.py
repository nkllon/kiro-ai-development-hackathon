from src.rm_ddd.core.health import ModuleHealth

    def __init__(self):
        """Initialize logging infrastructure"""
        super().__init__(module_id="logginginfrastructure", version="1.0.0")
        register_module(self)
    