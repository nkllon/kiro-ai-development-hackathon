from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, name: str, validator: Callable, error_message: str):
        self.name = name
        self.validator = validator
        self.error_message = error_message
    