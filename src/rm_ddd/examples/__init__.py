"""
Reference implementations and examples for RM-DDD patterns.

This module provides comprehensive examples demonstrating systematic
domain-driven design patterns with RM compliance and best practices.
"""

from .ecommerce import (
    Product,
    Customer,
    Order,
    OrderItem,
    ShoppingCart,
    Money,
    ProductCatalogService,
    OrderManagementService,
    ProductRepository,
    CustomerRepository,
    OrderRepository,
)

__all__ = [
    # E-commerce domain
    "Product",
    "Customer", 
    "Order",
    "OrderItem",
    "ShoppingCart",
    "Money",
    "ProductCatalogService",
    "OrderManagementService",
    "ProductRepository",
    "CustomerRepository",
    "OrderRepository",
]