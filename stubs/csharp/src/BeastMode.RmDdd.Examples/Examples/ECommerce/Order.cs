using System;
using System.Collections.Generic;
using System.Linq;
using BeastMode.RmDdd.Domain;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Examples.ECommerce
{
    /// <summary>
    /// Order aggregate root demonstrating proper DDD patterns in C#.
    /// Shows how to implement domain logic, invariants, and event generation following .NET conventions.
    /// </summary>
    public class Order : AggregateRoot<OrderId>
    {
        private readonly List<OrderLine> _orderLines = new();
        
        public CustomerId CustomerId { get; private set; }
        public IReadOnlyList<OrderLine> OrderLines => _orderLines.AsReadOnly();
        public OrderStatus Status { get; private set; }
        public DateTimeOffset OrderDate { get; private set; }
        public decimal TotalAmount { get; private set; }
        
        public Order(OrderId id, CustomerId customerId) : base(id, "OrderManagement")
        {
            CustomerId = customerId ?? throw new ArgumentNullException(nameof(customerId));
            Status = OrderStatus.Pending;
            OrderDate = DateTimeOffset.UtcNow;
            TotalAmount = 0m;
            
            // Generate domain event
            AddDomainEvent(new OrderCreatedEvent(id, customerId));
        }
        
        public void AddOrderLine(ProductId productId, int quantity, decimal unitPrice)
        {
            if (Status != OrderStatus.Pending)
            {
                throw new InvalidOperationException("Cannot modify order that is not pending");
            }
            
            var orderLine = new OrderLine(productId, quantity, unitPrice);
            _orderLines.Add(orderLine);
            RecalculateTotal();
            UpdateVersion();
            
            AddDomainEvent(new OrderLineAddedEvent(Id, productId, quantity, unitPrice));
        }
        
        public void RemoveOrderLine(ProductId productId)
        {
            if (Status != OrderStatus.Pending)
            {
                throw new InvalidOperationException("Cannot modify order that is not pending");
            }
            
            var removed = _orderLines.RemoveAll(line => line.ProductId.Equals(productId)) > 0;
            if (removed)
            {
                RecalculateTotal();
                UpdateVersion();
                AddDomainEvent(new OrderLineRemovedEvent(Id, productId));
            }
        }
        
        public void Confirm()
        {
            if (Status != OrderStatus.Pending)
            {
                throw new InvalidOperationException("Can only confirm pending orders");
            }
            
            if (!_orderLines.Any())
            {
                throw new InvalidOperationException("Cannot confirm order with no order lines");
            }
            
            Status = OrderStatus.Confirmed;
            UpdateVersion();
            
            AddDomainEvent(new OrderConfirmedEvent(Id, TotalAmount));
        }
        
        public void Cancel()
        {
            if (Status is OrderStatus.Shipped or OrderStatus.Delivered)
            {
                throw new InvalidOperationException("Cannot cancel shipped or delivered orders");
            }
            
            Status = OrderStatus.Cancelled;
            UpdateVersion();
            
            AddDomainEvent(new OrderCancelledEvent(Id));
        }
        
        private void RecalculateTotal()
        {
            TotalAmount = _orderLines.Sum(line => line.LineTotal);
        }
        
        public override DomainBoundaries GetDomainBoundaries()
        {
            return DomainBoundaries.Builder()
                .WithContext("OrderManagement")
                .WithAggregateType("Order")
                .WithCapability("order_creation")
                .WithCapability("order_modification")
                .WithCapability("order_confirmation")
                .WithConstraint("no_modification_after_confirmation")
                .WithConstraint("minimum_one_order_line")
                .Build();
        }
        
        public override AggregateBoundaries GetAggregateBoundaries()
        {
            return AggregateBoundaries.Builder()
                .WithAggregateType("Order")
                .WithEntityType("Order")
                .WithEntityType("OrderLine")
                .WithInvariant("order_must_have_customer")
                .WithInvariant("confirmed_order_must_have_lines")
                .WithInvariant("total_amount_must_match_lines")
                .WithMaxSize(50) // Maximum 50 order lines
                .WithEnforceConsistency(true)
                .Build();
        }
        
        protected override ValidationResult ValidateAggregateRules()
        {
            var result = new ValidationResult();
            
            // Validate customer ID
            if (CustomerId == null)
            {
                result.AddError("Order must have a customer");
            }
            
            // Validate order lines for confirmed orders
            if (Status == OrderStatus.Confirmed && !_orderLines.Any())
            {
                result.AddError("Confirmed order must have at least one order line");
            }
            
            // Validate total amount calculation
            var calculatedTotal = _orderLines.Sum(line => line.LineTotal);
            if (Math.Abs(TotalAmount - calculatedTotal) > 0.01m)
            {
                result.AddError("Total amount does not match sum of order lines");
            }
            
            // Validate aggregate size
            if (_orderLines.Count > 50)
            {
                result.AddError("Order cannot have more than 50 order lines");
            }
            
            return result;
        }
        
        public override ValidationResult ValidateDomainInvariants()
        {
            var result = base.ValidateDomainInvariants();
            
            // Additional entity-level validation
            if (OrderDate == default)
            {
                result.AddError("Order must have an order date");
            }
            
            if (TotalAmount < 0)
            {
                result.AddError("Order total amount cannot be negative");
            }
            
            return result;
        }
    }
}