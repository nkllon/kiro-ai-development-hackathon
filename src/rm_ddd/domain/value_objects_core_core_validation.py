"""
Value Objects Core Core Validation

This module was extracted from value_objects_core_core.py
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

@abstractmethod
def validate(self) -> ValidationResult:
    """
        Validate value object constraints.
        
        Returns:
            ValidationResult: Result of value object validation
            
        Note:
            This method must be implemented by all value objects to define
            their validation rules and constraints.
        """
    pass

def validate(self) -> ValidationResult:
    """Validate money value object."""
    result = ValidationResult(is_valid=True)
    if not isinstance(self.amount, Decimal):
        result.add_error('Amount must be a Decimal')
    if not self.currency or len(self.currency) != 3:
        result.add_error('Currency must be a 3-letter ISO code')
    if not self.currency.isalpha():
        result.add_error('Currency must contain only letters')
    return result

def validate(self) -> ValidationResult:
    """Validate email address format."""
    result = ValidationResult(is_valid=True)
    if not self.address:
        result.add_error('Email address cannot be empty')
        return result
    email_pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, self.address):
        result.add_error('Invalid email address format')
    if len(self.address) > 254:
        result.add_error('Email address too long (max 254 characters)')
    return result

def validate(self) -> ValidationResult:
    """Validate phone number format."""
    result = ValidationResult(is_valid=True)
    if not self.number:
        result.add_error('Phone number cannot be empty')
        return result
    if not re.match('^\\+?[\\d]{7,15}$', self.number):
        result.add_error('Invalid phone number format')
    if self.country_code and len(self.country_code) != 2:
        result.add_error('Country code must be 2 letters')
    return result

def validate(self) -> ValidationResult:
    """Validate address components."""
    result = ValidationResult(is_valid=True)
    if not self.street or not self.street.strip():
        result.add_error('Street address is required')
    if not self.city or not self.city.strip():
        result.add_error('City is required')
    if not self.country or len(self.country) != 2:
        result.add_error('Country must be a 2-letter ISO code')
    if self.country == 'US':
        if not self.state or len(self.state) != 2:
            result.add_error('US addresses must have a 2-letter state code')
        if self.postal_code and (not re.match('^\\d{5}(-\\d{4})?$', self.postal_code)):
            result.add_error('US postal code must be in format 12345 or 12345-6789')
    return result

def validate(self) -> ValidationResult:
    """Validate date range."""
    result = ValidationResult(is_valid=True)
    if not isinstance(self.start_date, date):
        result.add_error('Start date must be a date object')
    if not isinstance(self.end_date, date):
        result.add_error('End date must be a date object')
    if self.start_date > self.end_date:
        result.add_error('Start date must be before or equal to end date')
    return result

def validate(self) -> ValidationResult:
    """Validate percentage value."""
    result = ValidationResult(is_valid=True)
    if not isinstance(self.value, Decimal):
        result.add_error('Percentage value must be a Decimal')
    if self.value < 0 or self.value > 100:
        result.add_error('Percentage must be between 0 and 100')
    return result
