from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[Dict[str, Any]] = []
    