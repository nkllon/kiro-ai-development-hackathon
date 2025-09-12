"""
Value Objects Core Validation

This module was extracted from value_objects_core.py
as part of RM-DDD compliance refactoring.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4
from ...core.compliance import ValidationResult
from ...domain.value_objects import ImmutableValueObject
from ...utilities.decorators import value_object
import re
import re
import re
import re
import re

def validate(self) -> ValidationResult:
    """Validate money value object."""
    result = ValidationResult(is_valid=True)
    if self.amount < 0:
        result.add_error('Money amount cannot be negative')
    if not self.currency or len(self.currency) != 3:
        result.add_error('Currency must be a 3-letter ISO code')
    return result

def validate(self) -> ValidationResult:
    """Validate product ID."""
    result = ValidationResult(is_valid=True)
    if not isinstance(self.value, UUID):
        result.add_error('ProductId must be a valid UUID')
    return result

def validate(self) -> ValidationResult:
    """Validate customer ID."""
    result = ValidationResult(is_valid=True)
    if not isinstance(self.value, UUID):
        result.add_error('CustomerId must be a valid UUID')
    return result

def validate(self) -> ValidationResult:
    """Validate order ID."""
    result = ValidationResult(is_valid=True)
    if not isinstance(self.value, UUID):
        result.add_error('OrderId must be a valid UUID')
    return result

def validate(self) -> ValidationResult:
    """Validate email address."""
    result = ValidationResult(is_valid=True)
    if not self._is_valid_email(self.address):
        result.add_error('Invalid email address format')
    return result

def validate(self) -> ValidationResult:
    """Validate address."""
    result = ValidationResult(is_valid=True)
    if not self.street:
        result.add_error('Street address is required')
    if not self.city:
        result.add_error('City is required')
    if not self.state:
        result.add_error('State is required')
    if not self.postal_code:
        result.add_error('Postal code is required')
    if self.country == 'US':
        import re
        if not re.match('^\\d{5}(-\\d{4})?$', self.postal_code):
            result.add_error('Invalid US postal code format')
    return result

def validate(self) -> ValidationResult:
    """Validate quantity."""
    result = ValidationResult(is_valid=True)
    if self.value < 0:
        result.add_error('Quantity cannot be negative')
    return result
