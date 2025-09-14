"""
Value Objects Core Utils

This module was extracted from value_objects_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from decimal import Decimal
from datetime import datetime, date
import re
from ..core.compliance import ValidationResult
from ..models import DomainException, ValidationException

def get_formatted_address(self) -> str:
    """Get formatted address string."""
    parts = [self.street, self.city]
    if self.state:
        parts.append(self.state)
    if self.postal_code:
        parts.append(self.postal_code)
    parts.append(self.country)
    return ', '.join(parts)
