#!/usr/bin/env python3
"""
Exceptions
==========

Auto-generated module after cleanup.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Minimal valid module
"""

from typing import Dict, Any
from datetime import datetime


class BeastModeError(Exception):
    """Base exception for Beast Mode Framework."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.timestamp = datetime.now()
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class BeastModeConfigurationError(BeastModeError):
    """Configuration related errors."""
    pass


class BeastModeRuntimeError(BeastModeError):
    """Runtime related errors."""
    pass


class BeastModeValidationError(BeastModeError):
    """Validation related errors."""
    pass


class Exceptions:
    """Minimal valid class."""

    def __init__(self):
        self.module_id = "exceptions"
        self.timestamp = datetime.now()

    def get_info(self) -> Dict[str, Any]:
        """Get module info."""
        return {"module_id": self.module_id, "timestamp": self.timestamp.isoformat()}
