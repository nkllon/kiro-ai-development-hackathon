"""
Order domain model example.

This demonstrates basic DDD patterns using Kiro AI's framework.
"""

from typing import List, Dict, Any
from .value_objects import Money


class Order:
    """Order aggregate root."""
    
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items: List[Dict[str, Any]] = []
        self.status = "pending"
    
    def add_item(self, product_id: str, quantity: int, price: float) -> None:
        """Add item to order with domain validation."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        self.items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price": price
        })
    
    def get_total(self) -> Money:
        """Calculate order total."""
        total = sum(item["price"] * item["quantity"] for item in self.items)
        return Money(total, "USD")
    
    def confirm(self) -> None:
        """Confirm the order."""
        if not self.items:
            raise ValueError("Cannot confirm empty order")
        self.status = "confirmed"


class OrderService:
    """Order domain service."""
    
    @staticmethod
    def calculate_discount(order: Order) -> Money:
        """Calculate discount based on order total."""
        total = order.get_total()
        
        # Simple discount logic
        if total.amount >= 100:
            return Money(total.amount * 0.1, "USD")  # 10% discount
        elif total.amount >= 50:
            return Money(total.amount * 0.05, "USD")  # 5% discount
        else:
            return Money(0, "USD")
    
    @staticmethod
    def calculate_final_total(order: Order) -> Money:
        """Calculate final total after discount."""
        total = order.get_total()
        discount = OrderService.calculate_discount(order)
        return Money(total.amount - discount.amount, "USD")
