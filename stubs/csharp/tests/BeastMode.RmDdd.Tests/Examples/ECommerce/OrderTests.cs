using BeastMode.RmDdd.Examples.ECommerce;
using BeastMode.RmDdd.Examples.ECommerce.Events;
using FluentAssertions;
using Xunit;

namespace BeastMode.RmDdd.Tests.Examples.ECommerce
{
    /// <summary>
    /// Unit tests for Order aggregate demonstrating proper testing patterns for RM-DDD components.
    /// </summary>
    public class OrderTests
    {
        [Fact]
        public void Order_WhenCreated_ShouldHaveCorrectInitialState()
        {
            // Arrange
            var orderId = OrderId.Generate();
            var customerId = CustomerId.Generate();
            
            // Act
            var order = new Order(orderId, customerId);
            
            // Assert
            order.Id.Should().Be(orderId);
            order.CustomerId.Should().Be(customerId);
            order.Status.Should().Be(OrderStatus.Pending);
            order.OrderLines.Should().BeEmpty();
            order.TotalAmount.Should().Be(0m);
            order.GetDomainEvents().Should().HaveCount(1);
            order.GetDomainEvents().First().Should().BeOfType<OrderCreatedEvent>();
        }
        
        [Fact]
        public void Order_WhenCreatedWithNullCustomerId_ShouldThrowArgumentNullException()
        {
            // Arrange
            var orderId = OrderId.Generate();
            
            // Act & Assert
            var act = () => new Order(orderId, null!);
            act.Should().Throw<ArgumentNullException>()
                .WithParameterName("customerId");
        }
        
        [Fact]
        public void AddOrderLine_WhenOrderIsPending_ShouldAddLineAndRecalculateTotal()
        {
            // Arrange
            var order = CreateTestOrder();
            var productId = ProductId.Generate();
            const int quantity = 2;
            const decimal unitPrice = 10.50m;
            
            // Act
            order.AddOrderLine(productId, quantity, unitPrice);
            
            // Assert
            order.OrderLines.Should().HaveCount(1);
            order.OrderLines.First().ProductId.Should().Be(productId);
            order.OrderLines.First().Quantity.Should().Be(quantity);
            order.OrderLines.First().UnitPrice.Should().Be(unitPrice);
            order.TotalAmount.Should().Be(21.00m);
            
            var domainEvents = order.GetDomainEvents();
            domainEvents.Should().HaveCount(2); // OrderCreated + OrderLineAdded
            domainEvents.Last().Should().BeOfType<OrderLineAddedEvent>();
        }
        
        [Fact]
        public void AddOrderLine_WhenOrderIsNotPending_ShouldThrowInvalidOperationException()
        {
            // Arrange
            var order = CreateTestOrder();
            order.AddOrderLine(ProductId.Generate(), 1, 10m);
            order.Confirm();
            
            // Act & Assert
            var act = () => order.AddOrderLine(ProductId.Generate(), 1, 10m);
            act.Should().Throw<InvalidOperationException>()
                .WithMessage("Cannot modify order that is not pending");
        }
        
        [Fact]
        public void RemoveOrderLine_WhenProductExists_ShouldRemoveLineAndRecalculateTotal()
        {
            // Arrange
            var order = CreateTestOrder();
            var productId = ProductId.Generate();
            order.AddOrderLine(productId, 2, 10m);
            order.AddOrderLine(ProductId.Generate(), 1, 5m);
            
            // Act
            order.RemoveOrderLine(productId);
            
            // Assert
            order.OrderLines.Should().HaveCount(1);
            order.TotalAmount.Should().Be(5m);
            
            var domainEvents = order.GetDomainEvents();
            domainEvents.OfType<OrderLineRemovedEvent>().Should().HaveCount(1);
        }
        
        [Fact]
        public void Confirm_WhenOrderHasLines_ShouldChangeStatusToConfirmed()
        {
            // Arrange
            var order = CreateTestOrder();
            order.AddOrderLine(ProductId.Generate(), 1, 10m);
            
            // Act
            order.Confirm();
            
            // Assert
            order.Status.Should().Be(OrderStatus.Confirmed);
            
            var domainEvents = order.GetDomainEvents();
            domainEvents.OfType<OrderConfirmedEvent>().Should().HaveCount(1);
        }
        
        [Fact]
        public void Confirm_WhenOrderHasNoLines_ShouldThrowInvalidOperationException()
        {
            // Arrange
            var order = CreateTestOrder();
            
            // Act & Assert
            var act = () => order.Confirm();
            act.Should().Throw<InvalidOperationException>()
                .WithMessage("Cannot confirm order with no order lines");
        }
        
        [Fact]
        public void Cancel_WhenOrderIsPendingOrConfirmed_ShouldChangeStatusToCancelled()
        {
            // Arrange
            var order = CreateTestOrder();
            
            // Act
            order.Cancel();
            
            // Assert
            order.Status.Should().Be(OrderStatus.Cancelled);
            
            var domainEvents = order.GetDomainEvents();
            domainEvents.OfType<OrderCancelledEvent>().Should().HaveCount(1);
        }
        
        [Fact]
        public void Cancel_WhenOrderIsShipped_ShouldThrowInvalidOperationException()
        {
            // Arrange
            var order = CreateTestOrder();
            // Simulate shipped status (would normally be done through a domain service)
            typeof(Order).GetProperty("Status")!.SetValue(order, OrderStatus.Shipped);
            
            // Act & Assert
            var act = () => order.Cancel();
            act.Should().Throw<InvalidOperationException>()
                .WithMessage("Cannot cancel shipped or delivered orders");
        }
        
        [Fact]
        public void ValidateDomainInvariants_WhenOrderIsValid_ShouldReturnValidResult()
        {
            // Arrange
            var order = CreateTestOrder();
            order.AddOrderLine(ProductId.Generate(), 1, 10m);
            
            // Act
            var result = order.ValidateDomainInvariants();
            
            // Assert
            result.IsValid.Should().BeTrue();
            result.Errors.Should().BeEmpty();
        }
        
        [Fact]
        public void ValidateDomainInvariants_WhenConfirmedOrderHasNoLines_ShouldReturnInvalidResult()
        {
            // Arrange
            var order = CreateTestOrder();
            // Force confirmed status without lines (invalid state)
            typeof(Order).GetProperty("Status")!.SetValue(order, OrderStatus.Confirmed);
            
            // Act
            var result = order.ValidateDomainInvariants();
            
            // Assert
            result.IsValid.Should().BeFalse();
            result.Errors.Should().Contain("Confirmed order must have at least one order line");
        }
        
        [Fact]
        public void GetDomainBoundaries_ShouldReturnCorrectBoundaries()
        {
            // Arrange
            var order = CreateTestOrder();
            
            // Act
            var boundaries = order.GetDomainBoundaries();
            
            // Assert
            boundaries.Context.Should().Be("OrderManagement");
            boundaries.AggregateType.Should().Be("Order");
            boundaries.HasCapability("order_creation").Should().BeTrue();
            boundaries.HasCapability("order_modification").Should().BeTrue();
            boundaries.HasCapability("order_confirmation").Should().BeTrue();
        }
        
        [Fact]
        public void GetAggregateBoundaries_ShouldReturnCorrectBoundaries()
        {
            // Arrange
            var order = CreateTestOrder();
            
            // Act
            var boundaries = order.GetAggregateBoundaries();
            
            // Assert
            boundaries.AggregateType.Should().Be("Order");
            boundaries.ContainsEntityType("Order").Should().BeTrue();
            boundaries.ContainsEntityType("OrderLine").Should().BeTrue();
            boundaries.MaxSize.Should().Be(50);
            boundaries.EnforceConsistency.Should().BeTrue();
        }
        
        private static Order CreateTestOrder()
        {
            return new Order(OrderId.Generate(), CustomerId.Generate());
        }
    }
}