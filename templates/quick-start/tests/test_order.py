"""
Tests for the order domain model.

This demonstrates testing patterns using Kiro AI's framework.
"""

import pytest
from src.domain import Order, OrderService, Money


class TestOrder:
    """Test cases for Order aggregate."""
    
    def test_create_order(self):
        """Test order creation."""
        order = Order("order-123", "customer-456")
        assert order.order_id == "order-123"
        assert order.customer_id == "customer-456"
        assert order.status == "pending"
        assert order.items == []
    
    def test_add_item(self):
        """Test adding items to order."""
        order = Order("order-123", "customer-456")
        order.add_item("product-789", 2, 29.99)
        
        assert len(order.items) == 1
        assert order.items[0]["product_id"] == "product-789"
        assert order.items[0]["quantity"] == 2
        assert order.items[0]["price"] == 29.99
    
    def test_add_item_validation(self):
        """Test item validation."""
        order = Order("order-123", "customer-456")
        
        # Test negative quantity
        with pytest.raises(ValueError, match="Quantity must be positive"):
            order.add_item("product-789", -1, 29.99)
        
        # Test negative price
        with pytest.raises(ValueError, match="Price cannot be negative"):
            order.add_item("product-789", 2, -29.99)
    
    def test_get_total(self):
        """Test order total calculation."""
        order = Order("order-123", "customer-456")
        order.add_item("product-789", 2, 29.99)
        order.add_item("product-101", 1, 15.50)
        
        total = order.get_total()
        expected_total = (2 * 29.99) + (1 * 15.50)
        
        assert total.amount == expected_total
        assert total.currency == "USD"
    
    def test_confirm_order(self):
        """Test order confirmation."""
        order = Order("order-123", "customer-456")
        order.add_item("product-789", 2, 29.99)
        order.confirm()
        
        assert order.status == "confirmed"
    
    def test_confirm_empty_order(self):
        """Test confirming empty order fails."""
        order = Order("order-123", "customer-456")
        
        with pytest.raises(ValueError, match="Cannot confirm empty order"):
            order.confirm()


class TestOrderService:
    """Test cases for OrderService."""
    
    def test_calculate_discount(self):
        """Test discount calculation."""
        # Test 10% discount for orders >= $100
        order = Order("order-123", "customer-456")
        order.add_item("product-789", 2, 50.00)  # Total: $100
        discount = OrderService.calculate_discount(order)
        assert discount.amount == 10.00
        
        # Test 5% discount for orders >= $50
        order = Order("order-124", "customer-456")
        order.add_item("product-789", 1, 50.00)  # Total: $50
        discount = OrderService.calculate_discount(order)
        assert discount.amount == 2.50
        
        # Test no discount for orders < $50
        order = Order("order-125", "customer-456")
        order.add_item("product-789", 1, 25.00)  # Total: $25
        discount = OrderService.calculate_discount(order)
        assert discount.amount == 0.00
    
    def test_calculate_final_total(self):
        """Test final total calculation."""
        order = Order("order-123", "customer-456")
        order.add_item("product-789", 2, 50.00)  # Total: $100
        
        final_total = OrderService.calculate_final_total(order)
        expected_final = 100.00 - 10.00  # $100 - 10% discount
        
        assert final_total.amount == expected_final
        assert final_total.currency == "USD"


class TestMoney:
    """Test cases for Money value object."""
    
    def test_create_money(self):
        """Test money creation."""
        money = Money(100.50, "USD")
        assert money.amount == 100.50
        assert money.currency == "USD"
    
    def test_money_validation(self):
        """Test money validation."""
        # Test negative amount
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Money(-100, "USD")
        
        # Test invalid currency
        with pytest.raises(ValueError, match="Currency must be a 3-letter code"):
            Money(100, "US")
    
    def test_money_operations(self):
        """Test money operations."""
        money1 = Money(100, "USD")
        money2 = Money(50, "USD")
        
        # Test addition
        result = money1.add(money2)
        assert result.amount == 150
        assert result.currency == "USD"
        
        # Test subtraction
        result = money1.subtract(money2)
        assert result.amount == 50
        assert result.currency == "USD"
        
        # Test multiplication
        result = money1.multiply(1.5)
        assert result.amount == 150
        assert result.currency == "USD"
    
    def test_money_equality(self):
        """Test money equality."""
        money1 = Money(100, "USD")
        money2 = Money(100, "USD")
        money3 = Money(100, "EUR")
        money4 = Money(50, "USD")
        
        assert money1 == money2
        assert money1 != money3
        assert money1 != money4
    
    def test_money_string_representation(self):
        """Test money string representation."""
        money = Money(100.50, "USD")
        assert str(money) == "USD 100.50"
        assert repr(money) == "Money(100.5, 'USD')"
