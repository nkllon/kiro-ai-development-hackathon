from src.rm_ddd.core.registry import register_module

    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationReport] = []
        self._initialize_default_rules()
    