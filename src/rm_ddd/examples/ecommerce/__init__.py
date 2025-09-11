"""
E-commerce domain reference implementation.

This module demonstrates a complete e-commerce domain using RM-DDD patterns,
including entities, aggregates, value objects, domain services, and repositories.
"""

from .entities import Product, Customer, Order, OrderItem
from .aggregates import ShoppingCart
from .value_objects import Money, ProductId, CustomerId, OrderId
from .services import ProductCatalogService, OrderManagementService
from .repositories import ProductRepository, CustomerRepository, OrderRepository
from .events import OrderCreated, OrderItemAdded, ProductAddedToCart

__all__ = [
    # Entities
    "Product",
    "Customer", 
    "Order",
    "OrderItem",
    
    # Aggregates
    "ShoppingCart",
    
    # Value Objects
    "Money",
    "ProductId",
    "CustomerId", 
    "OrderId",
    
    # Services
    "ProductCatalogService",
    "OrderManagementService",
    
    # Repositories
    "ProductRepository",
    "CustomerRepository",
    "OrderRepository",
    
    # Events
    "OrderCreated",
    "OrderItemAdded",
    "ProductAddedToCart",
]