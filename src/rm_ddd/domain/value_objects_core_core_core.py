"""
Value Objects Core Core Core

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

class ValueObject(ABC):
    """
    Abstract base class for value objects.
    
    Provides systematic implementation of DDD value object patterns with
    value-based equality, immutability enforcement, and domain validation.
    
    Key Responsibilities:
    - Value-based equality and hashing
    - Immutability enforcement
    - Domain validation and constraint checking
    - Serialization and deserialization support
    
    Accountability Chain:
    - Domain Expert: Responsible for value object constraints and validation rules
    - Value Object Owner: Responsible for specific value object implementation
    - DDD Framework: Responsible for value object pattern compliance
    """

    def __eq__(self, other: Any) -> bool:
        """
        Value-based equality comparison.
        
        Two value objects are equal if they are of the same type and
        have the same values for all attributes.
        """
        if not isinstance(other, type(self)):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """
        Hash based on all attribute values.
        
        Allows value objects to be used in sets and as dictionary keys
        while maintaining value-based equality semantics.
        """
        values = []
        for key, value in sorted(self.__dict__.items()):
            if isinstance(value, (list, dict)):
                if isinstance(value, list):
                    values.append(tuple(value))
                elif isinstance(value, dict):
                    values.append(tuple(sorted(value.items())))
            else:
                values.append(value)
        return hash(tuple(values))

    def __repr__(self) -> str:
        """String representation of value object."""
        attrs = ', '.join((f'{k}={v!r}' for k, v in self.__dict__.items()))
        return f'{self.__class__.__name__}({attrs})'

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert value object to dictionary representation."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ValueObject):
                result[key] = value.to_dict()
            elif isinstance(value, (datetime, date)):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValueObject':
        """
        Create value object from dictionary representation.
        
        Args:
            data: Dictionary containing value object data
            
        Returns:
            ValueObject instance created from the data
            
        Note:
            This is a basic implementation that should be overridden
            by specific value object classes for proper deserialization.
        """
        return cls(**data)

    def copy_with(self, **changes) -> 'ValueObject':
        """
        Create a copy of this value object with specified changes.
        
        Args:
            **changes: Attribute changes to apply to the copy
            
        Returns:
            New value object instance with the specified changes
        """
        current_data = self.to_dict()
        current_data.update(changes)
        return self.__class__.from_dict(current_data)

@dataclass(frozen=True)
class ImmutableValueObject(ValueObject):
    """
    Immutable value object base class using dataclasses.
    
    Provides automatic immutability enforcement through the frozen=True
    dataclass parameter, along with systematic validation and value semantics.
    
    Usage:
        @dataclass(frozen=True)
        class Money(ImmutableValueObject):
            amount: Decimal
            currency: str
            
            def validate(self) -> ValidationResult:
                result = ValidationResult(is_valid=True)
                if self.amount < 0:
                    result.add_error("Amount cannot be negative")
                if len(self.currency) != 3:
                    result.add_error("Currency must be 3-letter ISO code")
                return result
    """

    def __post_init__(self):
        """
        Validate value object after initialization.
        
        Automatically called by dataclass after object creation to ensure
        all value objects are valid upon construction.
        """
        validation_result = self.validate()
        if not validation_result.is_valid:
            raise ValidationException(validation_errors=validation_result.errors, context={'value_object_type': self.__class__.__name__, 'value_object_data': self.to_dict()})

@dataclass(frozen=True)
class Money(ImmutableValueObject):
    """
    Money value object with currency support.
    
    Represents monetary amounts with proper currency handling,
    arithmetic operations, and validation.
    """
    amount: Decimal
    currency: str

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        object.__setattr__(self, 'currency', self.currency.upper())
        super().__post_init__()

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

    def __add__(self, other: 'Money') -> 'Money':
        """Add two money amounts."""
        if not isinstance(other, Money):
            raise TypeError('Can only add Money to Money')
        if self.currency != other.currency:
            raise DomainException(f'Cannot add {self.currency} and {other.currency}', error_code='CURRENCY_MISMATCH')
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two money amounts."""
        if not isinstance(other, Money):
            raise TypeError('Can only subtract Money from Money')
        if self.currency != other.currency:
            raise DomainException(f'Cannot subtract {other.currency} from {self.currency}', error_code='CURRENCY_MISMATCH')
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
        """Multiply money amount by a number."""
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """Divide money amount by a number."""
        if divisor == 0:
            raise DomainException('Cannot divide by zero', error_code='DIVISION_BY_ZERO')
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def __str__(self) -> str:
        """String representation of money."""
        return f'{self.amount} {self.currency}'

    @property
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == 0

    @property
    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > 0

    @property
    def is_negative(self) -> bool:
        """Check if amount is negative."""
        return self.amount < 0

@dataclass(frozen=True)
class EmailAddress(ImmutableValueObject):
    """
    Email address value object with validation.
    
    Represents email addresses with proper format validation
    and normalization.
    """
    address: str

    def __post_init__(self):
        object.__setattr__(self, 'address', self.address.lower().strip())
        super().__post_init__()

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

    @property
    def local_part(self) -> str:
        """Get local part of email address (before @)."""
        return self.address.split('@')[0] if '@' in self.address else ''

    @property
    def domain_part(self) -> str:
        """Get domain part of email address (after @)."""
        return self.address.split('@')[1] if '@' in self.address else ''

    def __str__(self) -> str:
        """String representation of email address."""
        return self.address

@dataclass(frozen=True)
class PhoneNumber(ImmutableValueObject):
    """
    Phone number value object with validation and formatting.
    
    Represents phone numbers with country code support and
    format validation.
    """
    number: str
    country_code: Optional[str] = None

    def __post_init__(self):
        normalized = re.sub('[^\\d+]', '', self.number)
        object.__setattr__(self, 'number', normalized)
        if self.country_code:
            object.__setattr__(self, 'country_code', self.country_code.upper())
        super().__post_init__()

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

    def __str__(self) -> str:
        """String representation of phone number."""
        if self.country_code:
            return f'{self.number} ({self.country_code})'
        return self.number

@dataclass(frozen=True)
class Address(ImmutableValueObject):
    """
    Address value object with comprehensive address components.
    
    Represents physical addresses with validation and formatting
    support for different address formats.
    """
    street: str
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = 'US'

    def __post_init__(self):
        object.__setattr__(self, 'country', self.country.upper())
        super().__post_init__()

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

    def get_formatted_address(self) -> str:
        """Get formatted address string."""
        parts = [self.street, self.city]
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.country)
        return ', '.join(parts)

    def __str__(self) -> str:
        """String representation of address."""
        return self.get_formatted_address()

@dataclass(frozen=True)
class DateRange(ImmutableValueObject):
    """
    Date range value object with validation and utility methods.
    
    Represents date ranges with proper validation and
    range operation support.
    """
    start_date: date
    end_date: date

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

    @property
    def duration_days(self) -> int:
        """Get duration in days."""
        return (self.end_date - self.start_date).days

    def contains_date(self, check_date: date) -> bool:
        """Check if date is within this range."""
        return self.start_date <= check_date <= self.end_date

    def overlaps_with(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another range."""
        return self.start_date <= other.end_date and self.end_date >= other.start_date

    def __str__(self) -> str:
        """String representation of date range."""
        return f'{self.start_date} to {self.end_date}'

@dataclass(frozen=True)
class Percentage(ImmutableValueObject):
    """
    Percentage value object with validation and utility methods.
    
    Represents percentage values with proper validation and
    arithmetic operations.
    """
    value: Decimal

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, 'value', Decimal(str(self.value)))
        super().__post_init__()

    def validate(self) -> ValidationResult:
        """Validate percentage value."""
        result = ValidationResult(is_valid=True)
        if not isinstance(self.value, Decimal):
            result.add_error('Percentage value must be a Decimal')
        if self.value < 0 or self.value > 100:
            result.add_error('Percentage must be between 0 and 100')
        return result

    @property
    def as_decimal(self) -> Decimal:
        """Get percentage as decimal (e.g., 50% -> 0.5)."""
        return self.value / 100

    @property
    def as_fraction(self) -> Tuple[int, int]:
        """Get percentage as fraction (e.g., 50% -> (1, 2))."""
        decimal_value = self.as_decimal
        if decimal_value == 0:
            return (0, 1)
        elif decimal_value == 1:
            return (1, 1)
        else:
            return (int(self.value), 100)

    def __str__(self) -> str:
        """String representation of percentage."""
        return f'{self.value}%'

def create_money(amount: Union[int, float, str, Decimal], currency: str='USD') -> Money:
    """
    Create a Money value object with validation.
    
    Args:
        amount: The monetary amount
        currency: The currency code (default: USD)
        
    Returns:
        Money value object
        
    Raises:
        ValidationException: If the money value is invalid
    """
    return Money(Decimal(str(amount)), currency)

def create_email(address: str) -> EmailAddress:
    """
    Create an EmailAddress value object with validation.
    
    Args:
        address: The email address string
        
    Returns:
        EmailAddress value object
        
    Raises:
        ValidationException: If the email address is invalid
    """
    return EmailAddress(address)

def create_percentage(value: Union[int, float, str, Decimal]) -> Percentage:
    """
    Create a Percentage value object with validation.
    
    Args:
        value: The percentage value (0-100)
        
    Returns:
        Percentage value object
        
    Raises:
        ValidationException: If the percentage value is invalid
    """
    return Percentage(Decimal(str(value)))

def __eq__(self, other: Any) -> bool:
    """
        Value-based equality comparison.
        
        Two value objects are equal if they are of the same type and
        have the same values for all attributes.
        """
    if not isinstance(other, type(self)):
        return False
    return self.__dict__ == other.__dict__

def __hash__(self) -> int:
    """
        Hash based on all attribute values.
        
        Allows value objects to be used in sets and as dictionary keys
        while maintaining value-based equality semantics.
        """
    values = []
    for key, value in sorted(self.__dict__.items()):
        if isinstance(value, (list, dict)):
            if isinstance(value, list):
                values.append(tuple(value))
            elif isinstance(value, dict):
                values.append(tuple(sorted(value.items())))
        else:
            values.append(value)
    return hash(tuple(values))

def __repr__(self) -> str:
    """String representation of value object."""
    attrs = ', '.join((f'{k}={v!r}' for k, v in self.__dict__.items()))
    return f'{self.__class__.__name__}({attrs})'

def to_dict(self) -> Dict[str, Any]:
    """Convert value object to dictionary representation."""
    result = {}
    for key, value in self.__dict__.items():
        if isinstance(value, ValueObject):
            result[key] = value.to_dict()
        elif isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = str(value)
        else:
            result[key] = value
    return result

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ValueObject':
    """
        Create value object from dictionary representation.
        
        Args:
            data: Dictionary containing value object data
            
        Returns:
            ValueObject instance created from the data
            
        Note:
            This is a basic implementation that should be overridden
            by specific value object classes for proper deserialization.
        """
    return cls(**data)

def copy_with(self, **changes) -> 'ValueObject':
    """
        Create a copy of this value object with specified changes.
        
        Args:
            **changes: Attribute changes to apply to the copy
            
        Returns:
            New value object instance with the specified changes
        """
    current_data = self.to_dict()
    current_data.update(changes)
    return self.__class__.from_dict(current_data)

def __post_init__(self):
    """
        Validate value object after initialization.
        
        Automatically called by dataclass after object creation to ensure
        all value objects are valid upon construction.
        """
    validation_result = self.validate()
    if not validation_result.is_valid:
        raise ValidationException(validation_errors=validation_result.errors, context={'value_object_type': self.__class__.__name__, 'value_object_data': self.to_dict()})

def __post_init__(self):
    if not isinstance(self.amount, Decimal):
        object.__setattr__(self, 'amount', Decimal(str(self.amount)))
    object.__setattr__(self, 'currency', self.currency.upper())
    super().__post_init__()

def __add__(self, other: 'Money') -> 'Money':
    """Add two money amounts."""
    if not isinstance(other, Money):
        raise TypeError('Can only add Money to Money')
    if self.currency != other.currency:
        raise DomainException(f'Cannot add {self.currency} and {other.currency}', error_code='CURRENCY_MISMATCH')
    return Money(self.amount + other.amount, self.currency)

def __sub__(self, other: 'Money') -> 'Money':
    """Subtract two money amounts."""
    if not isinstance(other, Money):
        raise TypeError('Can only subtract Money from Money')
    if self.currency != other.currency:
        raise DomainException(f'Cannot subtract {other.currency} from {self.currency}', error_code='CURRENCY_MISMATCH')
    return Money(self.amount - other.amount, self.currency)

def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
    """Multiply money amount by a number."""
    return Money(self.amount * Decimal(str(multiplier)), self.currency)

def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
    """Divide money amount by a number."""
    if divisor == 0:
        raise DomainException('Cannot divide by zero', error_code='DIVISION_BY_ZERO')
    return Money(self.amount / Decimal(str(divisor)), self.currency)

def __str__(self) -> str:
    """String representation of money."""
    return f'{self.amount} {self.currency}'

@property
def is_zero(self) -> bool:
    """Check if amount is zero."""
    return self.amount == 0

@property
def is_positive(self) -> bool:
    """Check if amount is positive."""
    return self.amount > 0

@property
def is_negative(self) -> bool:
    """Check if amount is negative."""
    return self.amount < 0

def __post_init__(self):
    object.__setattr__(self, 'address', self.address.lower().strip())
    super().__post_init__()

@property
def local_part(self) -> str:
    """Get local part of email address (before @)."""
    return self.address.split('@')[0] if '@' in self.address else ''

@property
def domain_part(self) -> str:
    """Get domain part of email address (after @)."""
    return self.address.split('@')[1] if '@' in self.address else ''

def __str__(self) -> str:
    """String representation of email address."""
    return self.address

def __post_init__(self):
    normalized = re.sub('[^\\d+]', '', self.number)
    object.__setattr__(self, 'number', normalized)
    if self.country_code:
        object.__setattr__(self, 'country_code', self.country_code.upper())
    super().__post_init__()

def __str__(self) -> str:
    """String representation of phone number."""
    if self.country_code:
        return f'{self.number} ({self.country_code})'
    return self.number

def __post_init__(self):
    object.__setattr__(self, 'country', self.country.upper())
    super().__post_init__()

def __str__(self) -> str:
    """String representation of address."""
    return self.get_formatted_address()

@property
def duration_days(self) -> int:
    """Get duration in days."""
    return (self.end_date - self.start_date).days

def contains_date(self, check_date: date) -> bool:
    """Check if date is within this range."""
    return self.start_date <= check_date <= self.end_date

def overlaps_with(self, other: 'DateRange') -> bool:
    """Check if this range overlaps with another range."""
    return self.start_date <= other.end_date and self.end_date >= other.start_date

def __str__(self) -> str:
    """String representation of date range."""
    return f'{self.start_date} to {self.end_date}'

def __post_init__(self):
    if not isinstance(self.value, Decimal):
        object.__setattr__(self, 'value', Decimal(str(self.value)))
    super().__post_init__()

@property
def as_decimal(self) -> Decimal:
    """Get percentage as decimal (e.g., 50% -> 0.5)."""
    return self.value / 100

@property
def as_fraction(self) -> Tuple[int, int]:
    """Get percentage as fraction (e.g., 50% -> (1, 2))."""
    decimal_value = self.as_decimal
    if decimal_value == 0:
        return (0, 1)
    elif decimal_value == 1:
        return (1, 1)
    else:
        return (int(self.value), 100)

def __str__(self) -> str:
    """String representation of percentage."""
    return f'{self.value}%'

def __eq__(self, other: Any) -> bool:
    """
        Value-based equality comparison.
        
        Two value objects are equal if they are of the same type and
        have the same values for all attributes.
        """
    if not isinstance(other, type(self)):
        return False
    return self.__dict__ == other.__dict__

def __hash__(self) -> int:
    """
        Hash based on all attribute values.
        
        Allows value objects to be used in sets and as dictionary keys
        while maintaining value-based equality semantics.
        """
    values = []
    for key, value in sorted(self.__dict__.items()):
        if isinstance(value, (list, dict)):
            if isinstance(value, list):
                values.append(tuple(value))
            elif isinstance(value, dict):
                values.append(tuple(sorted(value.items())))
        else:
            values.append(value)
    return hash(tuple(values))

def __repr__(self) -> str:
    """String representation of value object."""
    attrs = ', '.join((f'{k}={v!r}' for k, v in self.__dict__.items()))
    return f'{self.__class__.__name__}({attrs})'

def to_dict(self) -> Dict[str, Any]:
    """Convert value object to dictionary representation."""
    result = {}
    for key, value in self.__dict__.items():
        if isinstance(value, ValueObject):
            result[key] = value.to_dict()
        elif isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = str(value)
        else:
            result[key] = value
    return result

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ValueObject':
    """
        Create value object from dictionary representation.
        
        Args:
            data: Dictionary containing value object data
            
        Returns:
            ValueObject instance created from the data
            
        Note:
            This is a basic implementation that should be overridden
            by specific value object classes for proper deserialization.
        """
    return cls(**data)

def copy_with(self, **changes) -> 'ValueObject':
    """
        Create a copy of this value object with specified changes.
        
        Args:
            **changes: Attribute changes to apply to the copy
            
        Returns:
            New value object instance with the specified changes
        """
    current_data = self.to_dict()
    current_data.update(changes)
    return self.__class__.from_dict(current_data)

def __post_init__(self):
    """
        Validate value object after initialization.
        
        Automatically called by dataclass after object creation to ensure
        all value objects are valid upon construction.
        """
    validation_result = self.validate()
    if not validation_result.is_valid:
        raise ValidationException(validation_errors=validation_result.errors, context={'value_object_type': self.__class__.__name__, 'value_object_data': self.to_dict()})

def __post_init__(self):
    if not isinstance(self.amount, Decimal):
        object.__setattr__(self, 'amount', Decimal(str(self.amount)))
    object.__setattr__(self, 'currency', self.currency.upper())
    super().__post_init__()

def __add__(self, other: 'Money') -> 'Money':
    """Add two money amounts."""
    if not isinstance(other, Money):
        raise TypeError('Can only add Money to Money')
    if self.currency != other.currency:
        raise DomainException(f'Cannot add {self.currency} and {other.currency}', error_code='CURRENCY_MISMATCH')
    return Money(self.amount + other.amount, self.currency)

def __sub__(self, other: 'Money') -> 'Money':
    """Subtract two money amounts."""
    if not isinstance(other, Money):
        raise TypeError('Can only subtract Money from Money')
    if self.currency != other.currency:
        raise DomainException(f'Cannot subtract {other.currency} from {self.currency}', error_code='CURRENCY_MISMATCH')
    return Money(self.amount - other.amount, self.currency)

def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
    """Multiply money amount by a number."""
    return Money(self.amount * Decimal(str(multiplier)), self.currency)

def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
    """Divide money amount by a number."""
    if divisor == 0:
        raise DomainException('Cannot divide by zero', error_code='DIVISION_BY_ZERO')
    return Money(self.amount / Decimal(str(divisor)), self.currency)

def __str__(self) -> str:
    """String representation of money."""
    return f'{self.amount} {self.currency}'

@property
def is_zero(self) -> bool:
    """Check if amount is zero."""
    return self.amount == 0

@property
def is_positive(self) -> bool:
    """Check if amount is positive."""
    return self.amount > 0

@property
def is_negative(self) -> bool:
    """Check if amount is negative."""
    return self.amount < 0

def __post_init__(self):
    object.__setattr__(self, 'address', self.address.lower().strip())
    super().__post_init__()

@property
def local_part(self) -> str:
    """Get local part of email address (before @)."""
    return self.address.split('@')[0] if '@' in self.address else ''

@property
def domain_part(self) -> str:
    """Get domain part of email address (after @)."""
    return self.address.split('@')[1] if '@' in self.address else ''

def __str__(self) -> str:
    """String representation of email address."""
    return self.address

def __post_init__(self):
    normalized = re.sub('[^\\d+]', '', self.number)
    object.__setattr__(self, 'number', normalized)
    if self.country_code:
        object.__setattr__(self, 'country_code', self.country_code.upper())
    super().__post_init__()

def __str__(self) -> str:
    """String representation of phone number."""
    if self.country_code:
        return f'{self.number} ({self.country_code})'
    return self.number

def __post_init__(self):
    object.__setattr__(self, 'country', self.country.upper())
    super().__post_init__()

def __str__(self) -> str:
    """String representation of address."""
    return self.get_formatted_address()

@property
def duration_days(self) -> int:
    """Get duration in days."""
    return (self.end_date - self.start_date).days

def contains_date(self, check_date: date) -> bool:
    """Check if date is within this range."""
    return self.start_date <= check_date <= self.end_date

def overlaps_with(self, other: 'DateRange') -> bool:
    """Check if this range overlaps with another range."""
    return self.start_date <= other.end_date and self.end_date >= other.start_date

def __str__(self) -> str:
    """String representation of date range."""
    return f'{self.start_date} to {self.end_date}'

def __post_init__(self):
    if not isinstance(self.value, Decimal):
        object.__setattr__(self, 'value', Decimal(str(self.value)))
    super().__post_init__()

@property
def as_decimal(self) -> Decimal:
    """Get percentage as decimal (e.g., 50% -> 0.5)."""
    return self.value / 100

@property
def as_fraction(self) -> Tuple[int, int]:
    """Get percentage as fraction (e.g., 50% -> (1, 2))."""
    decimal_value = self.as_decimal
    if decimal_value == 0:
        return (0, 1)
    elif decimal_value == 1:
        return (1, 1)
    else:
        return (int(self.value), 100)

def __str__(self) -> str:
    """String representation of percentage."""
    return f'{self.value}%'

def __eq__(self, other: Any) -> bool:
    """
        Value-based equality comparison.
        
        Two value objects are equal if they are of the same type and
        have the same values for all attributes.
        """
    if not isinstance(other, type(self)):
        return False
    return self.__dict__ == other.__dict__

def __hash__(self) -> int:
    """
        Hash based on all attribute values.
        
        Allows value objects to be used in sets and as dictionary keys
        while maintaining value-based equality semantics.
        """
    values = []
    for key, value in sorted(self.__dict__.items()):
        if isinstance(value, (list, dict)):
            if isinstance(value, list):
                values.append(tuple(value))
            elif isinstance(value, dict):
                values.append(tuple(sorted(value.items())))
        else:
            values.append(value)
    return hash(tuple(values))

def __repr__(self) -> str:
    """String representation of value object."""
    attrs = ', '.join((f'{k}={v!r}' for k, v in self.__dict__.items()))
    return f'{self.__class__.__name__}({attrs})'

def to_dict(self) -> Dict[str, Any]:
    """Convert value object to dictionary representation."""
    result = {}
    for key, value in self.__dict__.items():
        if isinstance(value, ValueObject):
            result[key] = value.to_dict()
        elif isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = str(value)
        else:
            result[key] = value
    return result

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ValueObject':
    """
        Create value object from dictionary representation.
        
        Args:
            data: Dictionary containing value object data
            
        Returns:
            ValueObject instance created from the data
            
        Note:
            This is a basic implementation that should be overridden
            by specific value object classes for proper deserialization.
        """
    return cls(**data)

def copy_with(self, **changes) -> 'ValueObject':
    """
        Create a copy of this value object with specified changes.
        
        Args:
            **changes: Attribute changes to apply to the copy
            
        Returns:
            New value object instance with the specified changes
        """
    current_data = self.to_dict()
    current_data.update(changes)
    return self.__class__.from_dict(current_data)

def __post_init__(self):
    """
        Validate value object after initialization.
        
        Automatically called by dataclass after object creation to ensure
        all value objects are valid upon construction.
        """
    validation_result = self.validate()
    if not validation_result.is_valid:
        raise ValidationException(validation_errors=validation_result.errors, context={'value_object_type': self.__class__.__name__, 'value_object_data': self.to_dict()})

def __post_init__(self):
    if not isinstance(self.amount, Decimal):
        object.__setattr__(self, 'amount', Decimal(str(self.amount)))
    object.__setattr__(self, 'currency', self.currency.upper())
    super().__post_init__()

def __add__(self, other: 'Money') -> 'Money':
    """Add two money amounts."""
    if not isinstance(other, Money):
        raise TypeError('Can only add Money to Money')
    if self.currency != other.currency:
        raise DomainException(f'Cannot add {self.currency} and {other.currency}', error_code='CURRENCY_MISMATCH')
    return Money(self.amount + other.amount, self.currency)

def __sub__(self, other: 'Money') -> 'Money':
    """Subtract two money amounts."""
    if not isinstance(other, Money):
        raise TypeError('Can only subtract Money from Money')
    if self.currency != other.currency:
        raise DomainException(f'Cannot subtract {other.currency} from {self.currency}', error_code='CURRENCY_MISMATCH')
    return Money(self.amount - other.amount, self.currency)

def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
    """Multiply money amount by a number."""
    return Money(self.amount * Decimal(str(multiplier)), self.currency)

def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
    """Divide money amount by a number."""
    if divisor == 0:
        raise DomainException('Cannot divide by zero', error_code='DIVISION_BY_ZERO')
    return Money(self.amount / Decimal(str(divisor)), self.currency)

def __str__(self) -> str:
    """String representation of money."""
    return f'{self.amount} {self.currency}'

@property
def is_zero(self) -> bool:
    """Check if amount is zero."""
    return self.amount == 0

@property
def is_positive(self) -> bool:
    """Check if amount is positive."""
    return self.amount > 0

@property
def is_negative(self) -> bool:
    """Check if amount is negative."""
    return self.amount < 0

def __post_init__(self):
    object.__setattr__(self, 'address', self.address.lower().strip())
    super().__post_init__()

@property
def local_part(self) -> str:
    """Get local part of email address (before @)."""
    return self.address.split('@')[0] if '@' in self.address else ''

@property
def domain_part(self) -> str:
    """Get domain part of email address (after @)."""
    return self.address.split('@')[1] if '@' in self.address else ''

def __str__(self) -> str:
    """String representation of email address."""
    return self.address

def __post_init__(self):
    normalized = re.sub('[^\\d+]', '', self.number)
    object.__setattr__(self, 'number', normalized)
    if self.country_code:
        object.__setattr__(self, 'country_code', self.country_code.upper())
    super().__post_init__()

def __str__(self) -> str:
    """String representation of phone number."""
    if self.country_code:
        return f'{self.number} ({self.country_code})'
    return self.number

def __post_init__(self):
    object.__setattr__(self, 'country', self.country.upper())
    super().__post_init__()

def __str__(self) -> str:
    """String representation of address."""
    return self.get_formatted_address()

@property
def duration_days(self) -> int:
    """Get duration in days."""
    return (self.end_date - self.start_date).days

def contains_date(self, check_date: date) -> bool:
    """Check if date is within this range."""
    return self.start_date <= check_date <= self.end_date

def overlaps_with(self, other: 'DateRange') -> bool:
    """Check if this range overlaps with another range."""
    return self.start_date <= other.end_date and self.end_date >= other.start_date

def __str__(self) -> str:
    """String representation of date range."""
    return f'{self.start_date} to {self.end_date}'

def __post_init__(self):
    if not isinstance(self.value, Decimal):
        object.__setattr__(self, 'value', Decimal(str(self.value)))
    super().__post_init__()

@property
def as_decimal(self) -> Decimal:
    """Get percentage as decimal (e.g., 50% -> 0.5)."""
    return self.value / 100

@property
def as_fraction(self) -> Tuple[int, int]:
    """Get percentage as fraction (e.g., 50% -> (1, 2))."""
    decimal_value = self.as_decimal
    if decimal_value == 0:
        return (0, 1)
    elif decimal_value == 1:
        return (1, 1)
    else:
        return (int(self.value), 100)

def __str__(self) -> str:
    """String representation of percentage."""
    return f'{self.value}%'
