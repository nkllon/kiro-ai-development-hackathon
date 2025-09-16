"""
Value objects for the quick start template.

This demonstrates value object patterns using Kiro AI's framework.
"""

from typing import Any


class Money:
    """Money value object."""
    
    def __init__(self, amount: float, currency: str):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        if not currency or len(currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        
        self.amount = amount
        self.currency = currency.upper()
    
    def add(self, other: 'Money') -> 'Money':
        """Add another money amount."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract another money amount."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        """Multiply by a factor."""
        return Money(self.amount * factor, self.currency)
    
    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.currency} {self.amount:.2f}"
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Money({self.amount}, '{self.currency}')"
