from datetime import datetime
from typing import Dict, List, Any

    def __init__(self, name: str, validator: Callable, error_message: str):
        self.name = name
        self.validator = validator
        self.error_message = error_message
    