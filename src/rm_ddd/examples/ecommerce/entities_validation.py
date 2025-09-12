"""
Entities Validation

This module was extracted from entities.py
as part of RM-DDD compliance refactoring.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from ...core.compliance import ValidationResult
from ...domain.entities import Entity
from ...models import DomainBoundaries, DomainException
from ...utilities.decorators import domain_entity
from .value_objects import ProductId, CustomerId, OrderId, Money, EmailAddress, Address, Quantity

def validate_domain_invariants(self) -> ValidationResult:
    """Validate Product domain invariants."""
    result = ValidationResult(is_valid=True)
    if not self.name or len(self.name.strip()) == 0:
        result.add_error('Product name cannot be empty')
    if not self.price.is_positive():
        result.add_error('Product price must be positive')
    if self.stock_quantity < 0:
        result.add_error('Stock quantity cannot be negative')
    if self.updated_at < self.created_at:
        result.add_error('Updated date cannot be before created date')
    return result

def validate_domain_invariants(self) -> ValidationResult:
    """Validate Customer domain invariants."""
    result = ValidationResult(is_valid=True)
    if not self.first_name or len(self.first_name.strip()) == 0:
        result.add_error('Customer first name cannot be empty')
    if not self.last_name or len(self.last_name.strip()) == 0:
        result.add_error('Customer last name cannot be empty')
    email_validation = self.email.validate()
    if not email_validation.is_valid:
        result.add_error(f'Invalid email: {email_validation.errors}')
    for address in self.shipping_addresses + self.billing_addresses:
        address_validation = address.validate()
        if not address_validation.is_valid:
            result.add_error(f'Invalid address: {address_validation.errors}')
    if self.updated_at < self.created_at:
        result.add_error('Updated date cannot be before created date')
    return result

def validate_domain_invariants(self) -> ValidationResult:
    """Validate OrderItem domain invariants."""
    result = ValidationResult(is_valid=True)
    if not self.quantity.is_positive():
        result.add_error('Order item quantity must be positive')
    if not self.unit_price.is_positive():
        result.add_error('Order item unit price must be positive')
    product_id_validation = self.product_id.validate()
    if not product_id_validation.is_valid:
        result.add_error(f'Invalid product ID: {product_id_validation.errors}')
    return result

def validate_domain_invariants(self) -> ValidationResult:
    """Validate Order domain invariants."""
    result = ValidationResult(is_valid=True)
    customer_id_validation = self.customer_id.validate()
    if not customer_id_validation.is_valid:
        result.add_error(f'Invalid customer ID: {customer_id_validation.errors}')
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    if self.status not in valid_statuses:
        result.add_error(f'Invalid order status: {self.status}')
    if self.status in ['confirmed', 'shipped', 'delivered'] and (not self.items):
        result.add_error('Confirmed order must have items')
    if self.status in ['confirmed', 'shipped', 'delivered'] and (not self.shipping_address):
        result.add_error('Confirmed order must have shipping address')
    for item in self.items:
        item_validation = item.validate_domain_invariants()
        if not item_validation.is_valid:
            result.add_error(f'Invalid order item: {item_validation.errors}')
    if self.shipping_address:
        shipping_validation = self.shipping_address.validate()
        if not shipping_validation.is_valid:
            result.add_error(f'Invalid shipping address: {shipping_validation.errors}')
    if self.billing_address:
        billing_validation = self.billing_address.validate()
        if not billing_validation.is_valid:
            result.add_error(f'Invalid billing address: {billing_validation.errors}')
    if self.updated_at < self.created_at:
        result.add_error('Updated date cannot be before created date')
    if self.confirmed_at and self.confirmed_at < self.created_at:
        result.add_error('Confirmed date cannot be before created date')
    if self.shipped_at and self.confirmed_at and (self.shipped_at < self.confirmed_at):
        result.add_error('Shipped date cannot be before confirmed date')
    if self.delivered_at and self.shipped_at and (self.delivered_at < self.shipped_at):
        result.add_error('Delivered date cannot be before shipped date')
    return result
