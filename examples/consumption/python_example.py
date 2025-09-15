#!/usr/bin/env python3
"""
Example: How to consume the RM-DDD implementation in Python
Demonstrates practical usage of the systematic patterns we built.
"""

from rm_ddd.core import DomainReflectiveModule
from rm_ddd.domain import AggregateRoot, ValueObject, DomainService
from rm_ddd.utilities import ValidationResult
from rm_ddd.examples.ecommerce import Order, OrderId, CustomerId, ProductId


# Example 1: Create a new domain using RM-DDD patterns
class BookingId(ValueObject):
    """Example value object following RM-DDD patterns"""

    def __init__(self, value: str):
        self.value = value
        self.validate_on_construction()

    def validate(self) -> ValidationResult:
        result = ValidationResult()
        if not self.value or len(self.value) < 5:
            result.add_error("Booking ID must be at least 5 characters")
        return result

    def get_equality_components(self):
        return [self.value]


class Booking(AggregateRoot[BookingId]):
    """Example aggregate root using RM-DDD patterns"""

    def __init__(self, booking_id: BookingId, customer_id: CustomerId):
        super().__init__(booking_id, "booking_management")
        self.customer_id = customer_id
        self.status = "pending"
        self.items = []

    def add_item(self, item_id: str, quantity: int):
        """Business logic with systematic validation"""
        if self.status != "pending":
            raise ValueError("Cannot modify confirmed booking")

        self.items.append({"item_id": item_id, "quantity": quantity})
        self.update_version()

        # Generate domain event (systematic pattern)
        from rm_ddd.domain.events import DomainEvent

        event = BookingItemAddedEvent(self.id, item_id, quantity)
        self.add_domain_event(event)

    def get_domain_boundaries(self):
        return {
            "context": "booking_management",
            "capabilities": ["booking_creation", "item_management"],
            "constraints": ["no_modification_after_confirmation"],
        }

    def validate_domain_invariants(self) -> ValidationResult:
        result = ValidationResult()
        if not self.customer_id:
            result.add_error("Booking must have a customer")
        return result


class BookingService(DomainService):
    """Example domain service using RM-DDD patterns"""

    def __init__(self):
        super().__init__("booking_processor", "booking_management")

    async def process_booking(self, booking: Booking) -> ValidationResult:
        """Systematic business logic processing"""

        # Validate using systematic patterns
        validation = booking.validate_domain_invariants()
        if not validation.is_valid:
            return validation

        # Apply business rules systematically
        booking.status = "confirmed"
        booking.update_version()

        return ValidationResult.success()

    def get_domain_boundaries(self):
        return {"context": "booking_management", "service_type": "booking_processor"}


# Example 2: Use existing e-commerce patterns
def demonstrate_ecommerce_usage():
    """Show how to use the built-in e-commerce examples"""

    # Create systematic domain objects
    order_id = OrderId.generate()
    customer_id = CustomerId.generate()
    product_id = ProductId.generate()

    # Create order using systematic patterns
    order = Order(order_id, customer_id)

    # Add items systematically
    order.add_order_line(product_id, quantity=2, unit_price=25.99)

    # Validate using systematic validation
    validation = order.validate_domain_invariants()
    print(f"Order validation: {validation.is_valid}")

    # Confirm order (business logic)
    order.confirm()

    # Check domain events (systematic event handling)
    events = order.get_domain_events()
    print(f"Generated {len(events)} domain events")

    return order


# Example 3: Health monitoring and RM compliance
async def demonstrate_health_monitoring():
    """Show systematic health monitoring"""

    booking_service = BookingService()

    # Get systematic health information
    health = await booking_service.get_module_status()
    print(f"Service health: {health.status}")
    print(f"Capabilities: {health.capabilities}")

    # Check RM compliance
    is_healthy = await booking_service.is_healthy()
    print(f"RM compliance: {is_healthy}")

    return health


if __name__ == "__main__":
    print("=== RM-DDD Python Consumption Example ===")

    # Demonstrate systematic domain creation
    booking_id = BookingId("BOOK-12345")
    customer_id = CustomerId.generate()
    booking = Booking(booking_id, customer_id)
    booking.add_item("ITEM-001", 2)

    print(f"Created booking: {booking.id.value}")
    print(f"Domain context: {booking.domain_context}")

    # Demonstrate e-commerce usage
    order = demonstrate_ecommerce_usage()
    print(f"Created order: {order.id}")

    # Demonstrate health monitoring
    import asyncio

    health = asyncio.run(demonstrate_health_monitoring())
    print(f"System health: {health}")

    print("\n✅ RM-DDD systematic patterns working correctly!")
