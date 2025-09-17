from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationReport] = []
        self._initialize_default_rules()
    