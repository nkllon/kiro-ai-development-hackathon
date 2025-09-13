"""
Value Objects Core Core Core

This module was extracted from value_objects_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Value_Objects - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for value_objects.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/rm_ddd/examples/ecommerce/value_objects_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.520231
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
import re
import re
import re
import re

@value_object(immutable=True)
@dataclass(frozen=True)
class Money(ImmutableValueObject):
    """Money value object with currency support."""
    amount: Decimal
    currency: str = 'USD'

    def __post_init__(self):
        super().__post_init__()
        if self.amount < 0:
            raise ValueError('Money amount cannot be negative')
        if not self.currency or len(self.currency) != 3:
            raise ValueError('Currency must be a 3-letter ISO code')

    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts."""
        if self.currency != other.currency:
            raise ValueError(f'Cannot add {self.currency} and {other.currency}')
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money amounts."""
        if self.currency != other.currency:
            raise ValueError(f'Cannot subtract {other.currency} from {self.currency}')
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError('Result cannot be negative')
        return Money(result_amount, self.currency)

    def multiply(self, multiplier: Decimal) -> 'Money':
        """Multiply money by a factor."""
        if multiplier < 0:
            raise ValueError('Multiplier cannot be negative')
        return Money(self.amount * multiplier, self.currency)

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == Decimal('0')

    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > Decimal('0')

    def validate(self) -> ValidationResult:
        """Validate money value object."""
        result = ValidationResult(is_valid=True)
        if self.amount < 0:
            result.add_error('Money amount cannot be negative')
        if not self.currency or len(self.currency) != 3:
            result.add_error('Currency must be a 3-letter ISO code')
        return result

    def __str__(self) -> str:
        return f'{self.amount} {self.currency}'

@value_object(immutable=True)
@dataclass(frozen=True)
class ProductId(ImmutableValueObject):
    """Product identifier value object."""
    value: UUID

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.value, UUID):
            raise ValueError('ProductId must be a valid UUID')

    @classmethod
    def generate(cls) -> 'ProductId':
        """Generate a new product ID."""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> 'ProductId':
        """Create ProductId from string."""
        try:
            return cls(UUID(id_string))
        except ValueError:
            raise ValueError(f'Invalid ProductId format: {id_string}')

    def validate(self) -> ValidationResult:
        """Validate product ID."""
        result = ValidationResult(is_valid=True)
        if not isinstance(self.value, UUID):
            result.add_error('ProductId must be a valid UUID')
        return result

    def __str__(self) -> str:
        return str(self.value)

@value_object(immutable=True)
@dataclass(frozen=True)
class CustomerId(ImmutableValueObject):
    """Customer identifier value object."""
    value: UUID

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.value, UUID):
            raise ValueError('CustomerId must be a valid UUID')

    @classmethod
    def generate(cls) -> 'CustomerId':
        """Generate a new customer ID."""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> 'CustomerId':
        """Create CustomerId from string."""
        try:
            return cls(UUID(id_string))
        except ValueError:
            raise ValueError(f'Invalid CustomerId format: {id_string}')

    def validate(self) -> ValidationResult:
        """Validate customer ID."""
        result = ValidationResult(is_valid=True)
        if not isinstance(self.value, UUID):
            result.add_error('CustomerId must be a valid UUID')
        return result

    def __str__(self) -> str:
        return str(self.value)

@value_object(immutable=True)
@dataclass(frozen=True)
class OrderId(ImmutableValueObject):
    """Order identifier value object."""
    value: UUID

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.value, UUID):
            raise ValueError('OrderId must be a valid UUID')

    @classmethod
    def generate(cls) -> 'OrderId':
        """Generate a new order ID."""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> 'OrderId':
        """Create OrderId from string."""
        try:
            return cls(UUID(id_string))
        except ValueError:
            raise ValueError(f'Invalid OrderId format: {id_string}')

    def validate(self) -> ValidationResult:
        """Validate order ID."""
        result = ValidationResult(is_valid=True)
        if not isinstance(self.value, UUID):
            result.add_error('OrderId must be a valid UUID')
        return result

    def __str__(self) -> str:
        return str(self.value)

@value_object(immutable=True)
@dataclass(frozen=True)
class EmailAddress(ImmutableValueObject):
    """Email address value object with validation."""
    address: str

    def __post_init__(self):
        super().__post_init__()
        if not self._is_valid_email(self.address):
            raise ValueError(f'Invalid email address: {self.address}')

    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation."""
        import re
        pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @property
    def domain(self) -> str:
        """Get email domain."""
        return self.address.split('@')[1]

    @property
    def local_part(self) -> str:
        """Get email local part."""
        return self.address.split('@')[0]

    def validate(self) -> ValidationResult:
        """Validate email address."""
        result = ValidationResult(is_valid=True)
        if not self._is_valid_email(self.address):
            result.add_error('Invalid email address format')
        return result

    def __str__(self) -> str:
        return self.address

@value_object(immutable=True)
@dataclass(frozen=True)
class Address(ImmutableValueObject):
    """Address value object for shipping and billing."""
    street: str
    city: str
    state: str
    postal_code: str
    country: str = 'US'

    def __post_init__(self):
        super().__post_init__()
        if not all([self.street, self.city, self.state, self.postal_code]):
            raise ValueError('All address fields are required')

    def get_full_address(self) -> str:
        """Get formatted full address."""
        return f'{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}'

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

    def __str__(self) -> str:
        return self.get_full_address()

@value_object(immutable=True)
@dataclass(frozen=True)
class Quantity(ImmutableValueObject):
    """Quantity value object for order items."""
    value: int

    def __post_init__(self):
        super().__post_init__()
        if self.value < 0:
            raise ValueError('Quantity cannot be negative')

    def add(self, other: 'Quantity') -> 'Quantity':
        """Add two quantities."""
        return Quantity(self.value + other.value)

    def subtract(self, other: 'Quantity') -> 'Quantity':
        """Subtract two quantities."""
        result = self.value - other.value
        if result < 0:
            raise ValueError('Resulting quantity cannot be negative')
        return Quantity(result)

    def is_zero(self) -> bool:
        """Check if quantity is zero."""
        return self.value == 0

    def is_positive(self) -> bool:
        """Check if quantity is positive."""
        return self.value > 0

    def validate(self) -> ValidationResult:
        """Validate quantity."""
        result = ValidationResult(is_valid=True)
        if self.value < 0:
            result.add_error('Quantity cannot be negative')
        return result

    def __str__(self) -> str:
        return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if self.amount < 0:
        raise ValueError('Money amount cannot be negative')
    if not self.currency or len(self.currency) != 3:
        raise ValueError('Currency must be a 3-letter ISO code')

def add(self, other: 'Money') -> 'Money':
    """Add two money amounts."""
    if self.currency != other.currency:
        raise ValueError(f'Cannot add {self.currency} and {other.currency}')
    return Money(self.amount + other.amount, self.currency)

def subtract(self, other: 'Money') -> 'Money':
    """Subtract two money amounts."""
    if self.currency != other.currency:
        raise ValueError(f'Cannot subtract {other.currency} from {self.currency}')
    result_amount = self.amount - other.amount
    if result_amount < 0:
        raise ValueError('Result cannot be negative')
    return Money(result_amount, self.currency)

def multiply(self, multiplier: Decimal) -> 'Money':
    """Multiply money by a factor."""
    if multiplier < 0:
        raise ValueError('Multiplier cannot be negative')
    return Money(self.amount * multiplier, self.currency)

def is_zero(self) -> bool:
    """Check if amount is zero."""
    return self.amount == Decimal('0')

def is_positive(self) -> bool:
    """Check if amount is positive."""
    return self.amount > Decimal('0')

def __str__(self) -> str:
    return f'{self.amount} {self.currency}'

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('ProductId must be a valid UUID')

@classmethod
def generate(cls) -> 'ProductId':
    """Generate a new product ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'ProductId':
    """Create ProductId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid ProductId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('CustomerId must be a valid UUID')

@classmethod
def generate(cls) -> 'CustomerId':
    """Generate a new customer ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'CustomerId':
    """Create CustomerId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid CustomerId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('OrderId must be a valid UUID')

@classmethod
def generate(cls) -> 'OrderId':
    """Generate a new order ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'OrderId':
    """Create OrderId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid OrderId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not self._is_valid_email(self.address):
        raise ValueError(f'Invalid email address: {self.address}')

def _is_valid_email(self, email: str) -> bool:
    """Simple email validation."""
    import re
    pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@property
def domain(self) -> str:
    """Get email domain."""
    return self.address.split('@')[1]

@property
def local_part(self) -> str:
    """Get email local part."""
    return self.address.split('@')[0]

def __str__(self) -> str:
    return self.address

def __post_init__(self):
    super().__post_init__()
    if not all([self.street, self.city, self.state, self.postal_code]):
        raise ValueError('All address fields are required')

def get_full_address(self) -> str:
    """Get formatted full address."""
    return f'{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}'

def __str__(self) -> str:
    return self.get_full_address()

def __post_init__(self):
    super().__post_init__()
    if self.value < 0:
        raise ValueError('Quantity cannot be negative')

def add(self, other: 'Quantity') -> 'Quantity':
    """Add two quantities."""
    return Quantity(self.value + other.value)

def subtract(self, other: 'Quantity') -> 'Quantity':
    """Subtract two quantities."""
    result = self.value - other.value
    if result < 0:
        raise ValueError('Resulting quantity cannot be negative')
    return Quantity(result)

def is_zero(self) -> bool:
    """Check if quantity is zero."""
    return self.value == 0

def is_positive(self) -> bool:
    """Check if quantity is positive."""
    return self.value > 0

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if self.amount < 0:
        raise ValueError('Money amount cannot be negative')
    if not self.currency or len(self.currency) != 3:
        raise ValueError('Currency must be a 3-letter ISO code')

def add(self, other: 'Money') -> 'Money':
    """Add two money amounts."""
    if self.currency != other.currency:
        raise ValueError(f'Cannot add {self.currency} and {other.currency}')
    return Money(self.amount + other.amount, self.currency)

def subtract(self, other: 'Money') -> 'Money':
    """Subtract two money amounts."""
    if self.currency != other.currency:
        raise ValueError(f'Cannot subtract {other.currency} from {self.currency}')
    result_amount = self.amount - other.amount
    if result_amount < 0:
        raise ValueError('Result cannot be negative')
    return Money(result_amount, self.currency)

def multiply(self, multiplier: Decimal) -> 'Money':
    """Multiply money by a factor."""
    if multiplier < 0:
        raise ValueError('Multiplier cannot be negative')
    return Money(self.amount * multiplier, self.currency)

def is_zero(self) -> bool:
    """Check if amount is zero."""
    return self.amount == Decimal('0')

def is_positive(self) -> bool:
    """Check if amount is positive."""
    return self.amount > Decimal('0')

def __str__(self) -> str:
    return f'{self.amount} {self.currency}'

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('ProductId must be a valid UUID')

@classmethod
def generate(cls) -> 'ProductId':
    """Generate a new product ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'ProductId':
    """Create ProductId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid ProductId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('CustomerId must be a valid UUID')

@classmethod
def generate(cls) -> 'CustomerId':
    """Generate a new customer ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'CustomerId':
    """Create CustomerId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid CustomerId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('OrderId must be a valid UUID')

@classmethod
def generate(cls) -> 'OrderId':
    """Generate a new order ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'OrderId':
    """Create OrderId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid OrderId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not self._is_valid_email(self.address):
        raise ValueError(f'Invalid email address: {self.address}')

def _is_valid_email(self, email: str) -> bool:
    """Simple email validation."""
    import re
    pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@property
def domain(self) -> str:
    """Get email domain."""
    return self.address.split('@')[1]

@property
def local_part(self) -> str:
    """Get email local part."""
    return self.address.split('@')[0]

def __str__(self) -> str:
    return self.address

def __post_init__(self):
    super().__post_init__()
    if not all([self.street, self.city, self.state, self.postal_code]):
        raise ValueError('All address fields are required')

def get_full_address(self) -> str:
    """Get formatted full address."""
    return f'{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}'

def __str__(self) -> str:
    return self.get_full_address()

def __post_init__(self):
    super().__post_init__()
    if self.value < 0:
        raise ValueError('Quantity cannot be negative')

def add(self, other: 'Quantity') -> 'Quantity':
    """Add two quantities."""
    return Quantity(self.value + other.value)

def subtract(self, other: 'Quantity') -> 'Quantity':
    """Subtract two quantities."""
    result = self.value - other.value
    if result < 0:
        raise ValueError('Resulting quantity cannot be negative')
    return Quantity(result)

def is_zero(self) -> bool:
    """Check if quantity is zero."""
    return self.value == 0

def is_positive(self) -> bool:
    """Check if quantity is positive."""
    return self.value > 0

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if self.amount < 0:
        raise ValueError('Money amount cannot be negative')
    if not self.currency or len(self.currency) != 3:
        raise ValueError('Currency must be a 3-letter ISO code')

def add(self, other: 'Money') -> 'Money':
    """Add two money amounts."""
    if self.currency != other.currency:
        raise ValueError(f'Cannot add {self.currency} and {other.currency}')
    return Money(self.amount + other.amount, self.currency)

def subtract(self, other: 'Money') -> 'Money':
    """Subtract two money amounts."""
    if self.currency != other.currency:
        raise ValueError(f'Cannot subtract {other.currency} from {self.currency}')
    result_amount = self.amount - other.amount
    if result_amount < 0:
        raise ValueError('Result cannot be negative')
    return Money(result_amount, self.currency)

def multiply(self, multiplier: Decimal) -> 'Money':
    """Multiply money by a factor."""
    if multiplier < 0:
        raise ValueError('Multiplier cannot be negative')
    return Money(self.amount * multiplier, self.currency)

def is_zero(self) -> bool:
    """Check if amount is zero."""
    return self.amount == Decimal('0')

def is_positive(self) -> bool:
    """Check if amount is positive."""
    return self.amount > Decimal('0')

def __str__(self) -> str:
    return f'{self.amount} {self.currency}'

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('ProductId must be a valid UUID')

@classmethod
def generate(cls) -> 'ProductId':
    """Generate a new product ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'ProductId':
    """Create ProductId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid ProductId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('CustomerId must be a valid UUID')

@classmethod
def generate(cls) -> 'CustomerId':
    """Generate a new customer ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'CustomerId':
    """Create CustomerId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid CustomerId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not isinstance(self.value, UUID):
        raise ValueError('OrderId must be a valid UUID')

@classmethod
def generate(cls) -> 'OrderId':
    """Generate a new order ID."""
    return cls(uuid4())

@classmethod
def from_string(cls, id_string: str) -> 'OrderId':
    """Create OrderId from string."""
    try:
        return cls(UUID(id_string))
    except ValueError:
        raise ValueError(f'Invalid OrderId format: {id_string}')

def __str__(self) -> str:
    return str(self.value)

def __post_init__(self):
    super().__post_init__()
    if not self._is_valid_email(self.address):
        raise ValueError(f'Invalid email address: {self.address}')

def _is_valid_email(self, email: str) -> bool:
    """Simple email validation."""
    import re
    pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@property
def domain(self) -> str:
    """Get email domain."""
    return self.address.split('@')[1]

@property
def local_part(self) -> str:
    """Get email local part."""
    return self.address.split('@')[0]

def __str__(self) -> str:
    return self.address

def __post_init__(self):
    super().__post_init__()
    if not all([self.street, self.city, self.state, self.postal_code]):
        raise ValueError('All address fields are required')

def get_full_address(self) -> str:
    """Get formatted full address."""
    return f'{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}'

def __str__(self) -> str:
    return self.get_full_address()

def __post_init__(self):
    super().__post_init__()
    if self.value < 0:
        raise ValueError('Quantity cannot be negative')

def add(self, other: 'Quantity') -> 'Quantity':
    """Add two quantities."""
    return Quantity(self.value + other.value)

def subtract(self, other: 'Quantity') -> 'Quantity':
    """Subtract two quantities."""
    result = self.value - other.value
    if result < 0:
        raise ValueError('Resulting quantity cannot be negative')
    return Quantity(result)

def is_zero(self) -> bool:
    """Check if quantity is zero."""
    return self.value == 0

def is_positive(self) -> bool:
    """Check if quantity is positive."""
    return self.value > 0

def __str__(self) -> str:
    return str(self.value)
