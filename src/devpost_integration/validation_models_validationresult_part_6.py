from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, validation_data: Dict[str, Any] = None):
        """Initialize validation result."""
        super().__init__()
        self.module_id = "validation_result"
        self.version = "1.0.0"
        self.validation_data = validation_data or {}
        self.errors = []
        self.warnings = []
        self.is_valid = True
        self.validation_time = datetime.now()
        self._operation_count = 0
        self._errors = 0
        register_module(self)
    